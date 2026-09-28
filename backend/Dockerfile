FROM python:3.12-slim

WORKDIR /app

# Install system build dependencies needed for some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU-only PyTorch first (smaller image, faster build)
# Remove this line if GPU support is needed — just use the requirements.txt directly
RUN pip install --no-cache-dir \
    torch==2.1.0+cpu \
    torchvision==0.16.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Install remaining requirements (torch/torchvision already installed above)
RUN pip install --no-cache-dir \
    fastapi==0.116.1 \
    uvicorn[standard]==0.35.0 \
    SQLAlchemy==2.0.43 \
    "psycopg[binary]==3.2.9" \
    "python-jose[cryptography]==3.5.0" \
    "bcrypt>=4.0.0" \
    "pydantic[email]==2.11.7" \
    python-multipart==0.0.20 \
    "python-dotenv>=1.0.0" \
    "pillow>=10.0.0" \
    "numpy>=1.24.0,<2" \
    "opencv-python==4.10.0.84" \
    "scikit-learn>=1.2.0" \
    "pandas>=2.0.0" \
    "joblib>=1.3.0" \
    "reportlab>=3.6.0"

COPY app ./app

# Create directory for trained model (mounted from host via docker-compose volume)
RUN mkdir -p /app/app/ml/saved_models

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
