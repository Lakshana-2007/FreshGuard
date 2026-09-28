import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import get_current_user
from .database import get_db
from .ml.assessment import assess_freshness, is_model_ready
from .models import FreshnessAnalysis, User
from .reports import generate_freshness_pdf_report
from .schemas import AnalysisHistoryItem, FreshnessPredictionResponse

router = APIRouter(prefix="/analysis", tags=["analysis"])

_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}
_MAX_IMAGE_BYTES = 10 * 1024 * 1024


@router.post(
    "/predict",
    response_model=FreshnessPredictionResponse,
    status_code=status.HTTP_200_OK,
)
async def predict(
    file: UploadFile = File(...),
    item_name: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, WebP, and BMP images are supported",
        )

    image_bytes = await file.read(_MAX_IMAGE_BYTES + 1)
    if len(image_bytes) > _MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image must not exceed 10 MB",
        )

    if not is_model_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Freshness model is not available",
        )

    try:
        result = assess_freshness(image_bytes)
    except (FileNotFoundError, ModuleNotFoundError, RuntimeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Freshness model is not ready: {exc}",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image analysis failed: {exc}",
        ) from exc

    model_prediction = result["model_prediction"]
    visual_analysis = result["visual_analysis"]
    analysis = FreshnessAnalysis(
        user_id=current_user.id,
        item_name=item_name.strip() if item_name and item_name.strip() else model_prediction["food_item"],
        classification=result["classification"],
        confidence=result["confidence"],
        quality_score=result["quality_score"],
        spoilage_probability=result["spoilage_probability"],
        predicted_class=model_prediction["predicted_class"],
        color_metrics=json.dumps(visual_analysis["color"], default=float),
        texture_metrics=json.dumps(visual_analysis["texture"], default=float),

    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    result["id"] = analysis.id
    return result


@router.get("/history", response_model=list[AnalysisHistoryItem])
def history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list(
        db.scalars(
            select(FreshnessAnalysis)
            .where(FreshnessAnalysis.user_id == current_user.id)
            .order_by(FreshnessAnalysis.created_at.desc())
        )
    )


@router.get("/{analysis_id}/report")
def get_analysis_report(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if analysis_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Analysis ID must be a positive integer",
        )

    analysis = db.get(FreshnessAnalysis, analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis record not found",
        )

    # Authorization logic: owner OR administrator/food_quality_inspector role
    is_owner = analysis.user_id == current_user.id
    is_authorized_role = current_user.role in {"administrator", "food_quality_inspector"}
    if not (is_owner or is_authorized_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to download this analysis report",
        )

    try:
        pdf_bytes = generate_freshness_pdf_report(analysis, current_user)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report PDF: {exc}",
        ) from exc

    filename = f"FreshGuard_Report_{analysis_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )

