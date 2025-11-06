# News Credibility Analyzer

A real-time news credibility analysis service with keyword-based scoring, designed for easy extension with transformer models. Includes full CI/CD pipeline with Jenkins, Podman containerization, and automated versioning.

## Features

- **Real-time Analysis**: Analyze news articles for credibility instantly
- **Keyword-based Scoring**: Uses heuristics to detect credible vs. suspicious content
- **Extensible Architecture**: Designed to easily integrate transformer models
- **CI/CD Pipeline**: Automated build, test, tag, push, and deploy with Jenkins
- **Versioning**: Automatic versioning based on build number and git commit
- **Health Monitoring**: Built-in health check endpoints

## Project Structure

```
news-analyzer/
├── app/
│   ├── main.py              # Flask application
│   ├── model.py             # Credibility analysis logic
│   ├── templates/
│   │   └── dashboard.html   # Web UI
│   └── static/              # Static assets
├── tests/
│   └── test_api.py          # API tests
├── Dockerfile               # Container image definition
├── requirements.txt         # Python dependencies
├── Jenkinsfile             # CI/CD pipeline
├── README.md               # This file
└── deployment_history.log  # Deployment log (auto-generated)
```

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python -m app.main
   ```

3. **Access the dashboard:**
   - Open http://localhost:5000 in your browser

4. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

### Using Podman/Docker

1. **Build the image:**
   ```bash
   podman build -t news-credibility-analyzer:latest .
   # or
   docker build -t news-credibility-analyzer:latest .
   ```

2. **Run the container:**
   ```bash
   podman run -d -p 5000:5000 --name news-analyzer news-credibility-analyzer:latest
   # or
   docker run -d -p 5000:5000 --name news-analyzer news-credibility-analyzer:latest
   ```

3. **Check health:**
   ```bash
   curl http://localhost:5000/api/health
   ```

## API Endpoints

### `GET /`
Main dashboard page with web UI.

### `POST /api/analyze`
Analyze a news article for credibility.

**Request:**
```json
{
  "title": "Article title",
  "content": "Article content",
  "source": "Source name (optional)"
}
```

**Response:**
```json
{
  "credibility_score": 75.5,
  "risk_factors": ["No significant risk factors identified"],
  "recommendations": ["✓ Relatively high credibility", "Still recommended to verify with multiple sources"],
  "analysis_details": {
    "credible_indicators": 3,
    "suspicious_indicators": 0,
    "emotional_manipulation": 0,
    "source_credibility": 1.0
  },
  "timestamp": "2025-06-11T22:00:00Z",
  "version": "1.0.0"
}
```

### `GET /api/health`
Health check endpoint.

### `GET /api/version`
Get application version.

## CI/CD Pipeline

The Jenkins pipeline automates the following steps:

1. **Checkout**: Get latest code from repository
2. **Test**: Run pytest with coverage
3. **Build Image**: Build Podman/Docker image
4. **Tag Image**: Tag with version and latest
5. **Push to Registry**: Push to container registry
6. **Deploy**: Deploy new container
7. **Log Deployment**: Record deployment in log file

### Jenkins Setup

1. **Install Jenkins Plugins:**
   - Pipeline
   - Docker/Podman Pipeline (if needed)

2. **Configure Credentials:**
   - Add registry credentials with ID `registry-credentials`
   - Username/password for your container registry

3. **Create Pipeline Job:**
   - New Item → Pipeline
   - Point to Jenkinsfile in repository
   - Configure SCM (Git)

4. **Run Pipeline:**
   - Build Now
   - Monitor in Jenkins console

### Versioning

Versions are automatically generated as: `{BUILD_NUMBER}.{GIT_COMMIT_SHORT}`
- Example: `42.a1b2c3d`

Versions are:
- Set as image tags
- Included in API responses
- Logged in deployment_history.log

## Local Registry Setup (Optional)

For local testing with Podman:

```bash
# Start local registry
podman run -d -p 5000:5000 --name registry docker.io/library/registry:2

# Update Jenkinsfile REGISTRY to: localhost:5000
```

## Extending with Transformers

The architecture is designed for easy extension. To add transformer-based analysis:

1. **Update `app/model.py`:**
   ```python
   class NewsCredibilityAnalyzer:
       def __init__(self):
           # Existing keyword-based logic
           ...
           # Add transformer model loading
           self.transformer_model = load_transformer_model()
       
       def analyze(self, title, content, source=''):
           # Combine keyword and transformer scores
           keyword_score = self._keyword_analysis(...)
           transformer_score = self._transformer_analysis(...)
           # Weighted combination
           ...
   ```

2. **Update `requirements.txt`:**
   ```
   transformers==4.35.0
   torch==2.1.0
   ```

3. **Update Dockerfile:**
   - Add model download step
   - Increase image size if needed

## Testing

Run all tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ -v --cov=app --cov-report=html
```

## Deployment History

Deployment history is automatically logged to `deployment_history.log`:
```
2025-06-11 22:00:00 UTC | Version: 1.42.a1b2c3d | Build: 42 | Commit: a1b2c3d | Status: SUCCESS
```

## Environment Variables

- `PORT`: Server port (default: 5000)
- `APP_VERSION`: Application version (default: 1.0.0)
- `DEBUG`: Enable debug mode (default: False)

## Troubleshooting

### Container won't start
- Check logs: `podman logs news-analyzer`
- Verify port 5000 is available
- Check health endpoint: `curl http://localhost:5000/api/health`

### Jenkins pipeline fails
- Verify Podman/Docker is installed and accessible
- Check registry credentials are correct
- Review Jenkins console output for specific errors

### Tests fail
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Run tests in virtual environment

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

