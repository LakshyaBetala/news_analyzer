import os
import sys
from datetime import datetime, timezone
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator

# Handle imports for both local execution and Docker
try:
    from .model import NewsCredibilityAnalyzer
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.model import NewsCredibilityAnalyzer

# Initialize App
app = FastAPI(
    title="News Credibility Analyzer",
    description="Real-time news credibility analysis with MLOps monitoring",
    version=os.getenv('APP_VERSION', '1.0.0')
)

# --- MLOPS MAGIC STARTS HERE ---
# This line automatically tracks every request and exposes data at /metrics
# Prometheus will scrape this endpoint to build your Grafana dashboards.
Instrumentator().instrument(app).expose(app)
# -------------------------------

# Initialize Model
analyzer = NewsCredibilityAnalyzer()
templates = Jinja2Templates(directory="app/templates")

# Define Data Model (Replaces manual JSON parsing)
class NewsRequest(BaseModel):
    title: str = ""
    content: str = ""
    source: str = ""

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main dashboard page."""
    return templates.TemplateResponse(
        "dashboard.html", 
        {"request": request, "version": app.version}
    )

@app.post("/api/analyze")
async def analyze_news(request: NewsRequest):
    """
    Analyze news article for credibility.
    FastAPI automatically validates the JSON against NewsRequest model.
    """
    if not request.title and not request.content:
        raise HTTPException(status_code=400, detail="Title or content is required")
    
    try:
        # Run analysis
        result = analyzer.analyze(request.title, request.content, request.source)
        
        # Add MLOps metadata
        result['timestamp'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        result['version'] = app.version
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health():
    """Health check endpoint for Kubernetes."""
    return {
        "status": "healthy",
        "version": app.version,
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }

@app.get("/api/version")
async def version():
    return {
        "version": app.version,
        "service": "news-credibility-analyzer"
    }

# Entry point for debugging
if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', 5000))
    # Uvicorn is the server that runs FastAPI
    uvicorn.run(app, host='0.0.0.0', port=port)