# News Credibility Analyzer - Podman/Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# gcc is often needed for installing python packages like psutil/numpy
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV APP_VERSION=1.0.0

# Expose port (FastAPI default)
EXPOSE 8000

# Health check
# We use curl (installed above) or python for the check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"

# Run application with Uvicorn (The ASGI Server)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]