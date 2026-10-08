import json
import os
import sys
from datetime import datetime, timezone

# 1. Import FastAPI tools
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator

# Handle imports (same as before)
try:
    from .model import NewsCredibilityAnalyzer
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.model import NewsCredibilityAnalyzer

# 2. Initialize the App
app = FastAPI(
    title="News Credibility Analyzer",
    description="A real-time ML service to score news credibility.",
    version=os.getenv('APP_VERSION', '1.0.0')
)

# 3. Setup Monitoring (Prometheus)
# This automatically creates a /metrics endpoint that Prometheus will scrape later
Instrumentator().instrument(app).expose(app)

# Initialize your ML Logic
analyzer = NewsCredibilityAnalyzer()
VERSION = os.getenv('APP_VERSION', '1.0.0')

# 4. Define the Data "Schema" (Pydantic)
# This is the "Contract". The user MUST send data looking like this.
class NewsRequest(BaseModel):
    title: str
    content: str
    source: str = ""  # Optional, defaults to empty string

    # Example for the auto-generated docs
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Aliens Land in Times Square",
                "content": "Scientists confirm UFO sighting in New York...",
                "source": "Galaxy News"
            }
        }

# 5. Define the Response "Schema" (Optional but good practice)
class AnalysisResponse(BaseModel):
    credibility_score: float
    risk_factors: list[str]
    recommendations: list[str]
    analysis_details: dict = {}
    timestamp: str
    version: str

# --- ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serves the dashboard (if you still want the UI)."""
    # Note: For a pure API, we usually don't serve HTML, 
    # but we keep this for your project continuity.
    templates = Jinja2Templates(directory="app/templates")
    return templates.TemplateResponse(request, "dashboard.html", {"version": VERSION})

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_news(request: NewsRequest):
    """
    Analyzes a news article.
    FastAPI automatically validates that 'request' matches 'NewsRequest'.
    """
    try:
        # We access data directly like an object: request.title
        result = analyzer.analyze(request.title, request.content, request.source)
        
        # Add metadata
        result['timestamp'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        result['version'] = VERSION
        
        return result
    
    except Exception as e:
        # In FastAPI, we raise HTTP exceptions instead of returning JSON manually
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Simple health check for Kubernetes/Docker."""
    return {
        "status": "healthy",
        "version": VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }

def _load_releases() -> list:
    """Release history written by the Jenkins pipeline: S3 (S3_BUCKET) or a local file."""
    bucket = os.getenv("S3_BUCKET")
    try:
        if bucket:
            import boto3
            endpoint = os.getenv("S3_ENDPOINT_URL")  # set only when running against LocalStack
            extra = {"endpoint_url": endpoint, "aws_access_key_id": "test", "aws_secret_access_key": "test"} if endpoint else {}
            body = boto3.client("s3", **extra).get_object(Bucket=bucket, Key="releases.json")["Body"].read()
            return json.loads(body)
        path = os.getenv("RELEASES_FILE", "releases.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass  # no history yet (or S3 unreachable): show an empty control room
    return []


@app.get("/api/releases")
async def get_releases():
    return _load_releases()


@app.get("/releases", response_class=HTMLResponse)
async def releases_page(request: Request):
    templates = Jinja2Templates(directory="app/templates")
    return templates.TemplateResponse(request, "releases.html", {"version": VERSION})


@app.get("/api/version")
async def get_version():
    return {"version": VERSION, "service": "news-credibility-analyzer"}

# To run locally: uvicorn app.main:app --reload