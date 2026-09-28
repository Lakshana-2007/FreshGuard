import os
from contextlib import asynccontextmanager
from datetime import date, timedelta

from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .analysis import router as analysis_router
from .database import Base, engine, get_db
from .m3 import router as m3_router
from .models import User, FoodItem, ShelfLifePrediction
from .schemas import (
    RegisterRequest, LoginRequest, UserResponse, TokenResponse,
    FoodCreate, FoodResponse, ExpiringSoonItem, ROLES
)
from .auth import hash_password, verify_password, create_token, get_current_user
from .ml.assessment import is_model_ready


# A4: Replace deprecated @app.on_event("startup") with the modern lifespan pattern.
# Behaviour is identical: create all tables once on startup, continue in degraded
# mode if the database is unreachable.
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")
        print("App will continue running in degraded mode.")
    yield
    # Nothing to clean up on shutdown at this time.


app = FastAPI(
    title="AI Food Freshness Monitoring Platform API",
    version="1.0.0",
    description="Milestone 1 API: authentication and food inventory workflow.",
    lifespan=lifespan,
)

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router)
app.include_router(m3_router)

@app.get("/health")
def health():
    ready = is_model_ready()
    return {
        "status": "ok",
        "service": "food-freshness-api",
        "ml_available": ready,
        "model_status": "ready" if ready else "not_trained",
    }



@app.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    role = payload.role.lower()
    if role not in ROLES:
        raise HTTPException(400, "Invalid role")

    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing:
        raise HTTPException(409, "An account with this email already exists")

    user = User(
        full_name=payload.full_name.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return TokenResponse(
        access_token=create_token(user),
        user=user,
    )


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")

    return TokenResponse(
        access_token=create_token(user),
        user=user,
    )


@app.get("/auth/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/inventory", response_model=FoodResponse, status_code=status.HTTP_201_CREATED)
def create_food(
    payload: FoodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = FoodItem(**payload.model_dump(), created_by=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/inventory", response_model=list[FoodResponse])
def list_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list(
        db.scalars(
            select(FoodItem)
            .where(FoodItem.created_by == current_user.id)
            .order_by(FoodItem.created_at.desc())
        )
    )


# ============================================================
# B1 — Expiring-soon inventory endpoint
# ============================================================
# Registered before DELETE /inventory/{food_id} so FastAPI matches
# the fixed path segment "expiring-soon" before the int path parameter.

@app.get("/inventory/expiring-soon", response_model=list[ExpiringSoonItem])
def expiring_soon(
    days: int = Query(default=7, ge=1, le=365, description="Look-ahead window in days (1–365, default 7)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return inventory items whose expiry_date falls on or before today + `days`.

    Expired items (expiry_date < today) are always included — they are the most urgent.
    Results are ordered by expiry_date ascending (soonest / most overdue first).

    For each item the response includes the most recent M3 shelf-life prediction
    (risk_level, official_freshness_score, remaining_shelf_life_days) when one exists,
    and null for those fields when no prediction has been made yet.
    """
    today = date.today()
    cutoff = today + timedelta(days=days)

    items = list(db.scalars(
        select(FoodItem)
        .where(
            FoodItem.created_by == current_user.id,
            FoodItem.expiry_date <= cutoff,
        )
        .order_by(FoodItem.expiry_date.asc())
    ))

    if not items:
        return []

    # Fetch the most recent ShelfLifePrediction per food_item_id in one query.
    item_ids = [i.id for i in items]
    predictions_raw = list(db.scalars(
        select(ShelfLifePrediction)
        .where(
            ShelfLifePrediction.user_id == current_user.id,
            ShelfLifePrediction.food_item_id.in_(item_ids),
        )
        .order_by(ShelfLifePrediction.created_at.desc())
    ))
    # Keep only the newest prediction per item (results are already newest-first).
    latest_prediction: dict[int, ShelfLifePrediction] = {}
    for pred in predictions_raw:
        if pred.food_item_id not in latest_prediction:
            latest_prediction[pred.food_item_id] = pred

    result = []
    for item in items:
        days_until = (item.expiry_date - today).days
        pred = latest_prediction.get(item.id)
        result.append(ExpiringSoonItem(
            id=item.id,
            name=item.name,
            category=item.category,
            batch_number=item.batch_number,
            quantity=item.quantity,
            expiry_date=item.expiry_date,
            days_until_expiry=days_until,
            is_expired=days_until < 0,
            risk_level=pred.risk_level if pred else None,
            official_freshness_score=pred.official_freshness_score if pred else None,
            remaining_shelf_life_days=pred.remaining_shelf_life_days if pred else None,
        ))
    return result


@app.delete("/inventory/{food_id}")
def delete_food(
    food_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.scalar(
        select(FoodItem).where(
            FoodItem.id == food_id,
            FoodItem.created_by == current_user.id,
        )
    )
    if not item:
        raise HTTPException(404, "Food item not found")

    db.delete(item)
    db.commit()
    return {"message": "Food item deleted"}
