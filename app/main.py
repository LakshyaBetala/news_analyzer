"""CloudForge AI: FastAPI service for the news credibility analyzer, its Release Control Room and Platform pages."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, ConfigDict, Field

from .model import NewsCredibilityAnalyzer

HERE = Path(__file__).resolve().parent
VERSION = os.getenv("APP_VERSION", "1.0.0")

app = FastAPI(
    title="CloudForge AI · News Credibility Analyzer",
    description="Scores news articles for credibility; every release is quality-gated before deployment.",
    version=VERSION,
)
Instrumentator().instrument(app).expose(app)  # Prometheus metrics at /metrics

templates = Jinja2Templates(directory=HERE / "templates")
analyzer = NewsCredibilityAnalyzer()
# Demo articles for the dashboard's sample buttons, grouped by expected score band
SAMPLES = json.loads((HERE / "samples.json").read_text(encoding="utf-8"))


class NewsRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1, max_length=20_000)
    source: str = Field(default="", max_length=200)

    model_config = ConfigDict(json_schema_extra={"example": {
        "title": "Central bank holds interest rates steady",
        "content": "According to an official statement, the published data confirmed the findings.",
        "source": "Reuters",
    }})


class AnalysisResponse(BaseModel):
    credibility_score: float
    risk_factors: list[str]
    recommendations: list[str]
    analysis_details: dict = {}
    timestamp: str
    version: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html", {"version": VERSION, "samples": SAMPLES})


@app.get("/releases", response_class=HTMLResponse)
async def releases_page(request: Request):
    return templates.TemplateResponse(request, "releases.html", {"version": VERSION})


@app.get("/platform", response_class=HTMLResponse)
async def platform_page(request: Request):
    return templates.TemplateResponse(request, "platform.html", {
        "version": VERSION,
        "pod": os.getenv("HOSTNAME", "local"),  # Kubernetes sets HOSTNAME to the pod name
        "bucket": os.getenv("S3_BUCKET", ""),
        "target": "Local (LocalStack + k3s)" if os.getenv("S3_ENDPOINT_URL")
                  else "AWS (EC2 + k3s)" if os.getenv("S3_BUCKET") else "Developer machine",
    })


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_news(req: NewsRequest):
    try:
        result = analyzer.analyze(req.title, req.content, req.source)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {**result, "timestamp": _now(), "version": VERSION}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": VERSION, "timestamp": _now()}


@app.get("/api/version")
async def get_version():
    return {"version": VERSION, "service": "news-credibility-analyzer"}


@app.get("/api/releases")
async def get_releases():
    return _load_releases()
