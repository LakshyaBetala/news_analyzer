# Quick Start Guide - Copy-Paste Commands

## 🚀 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python -m app.main

# Run tests
pytest tests/ -v

# Access dashboard
# Open: http://localhost:5000
```

## 🐳 Podman Commands

```bash
# Build image
podman build -t news-credibility-analyzer:latest .

# Run container
podman run -d -p 5000:5000 --name news-analyzer news-credibility-analyzer:latest

# Check logs
podman logs news-analyzer

# Stop container
podman stop news-analyzer
podman rm news-analyzer
```

## 🧪 Test API

```bash
# Health check
curl http://localhost:5000/api/health

# Version
curl http://localhost:5000/api/version

# Analyze article
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Research Study Confirms Findings",
    "content": "Peer-reviewed study provides evidence.",
    "source": "Reuters"
  }'
```

## 📦 Registry Commands

```bash
# Start local registry
podman run -d -p 5000:5000 --name registry docker.io/library/registry:2

# Build and tag
podman build -t localhost:5000/news-credibility-analyzer:1.0.0 .
podman tag localhost:5000/news-credibility-analyzer:1.0.0 localhost:5000/news-credibility-analyzer:latest

# Push to registry
podman push localhost:5000/news-credibility-analyzer:1.0.0
podman push localhost:5000/news-credibility-analyzer:latest

# Pull from registry
podman pull localhost:5000/news-credibility-analyzer:1.0.0
```

## 🔧 Jenkins Setup

1. **Install Jenkins** (if needed):
   ```bash
   podman run -d -p 8080:8080 -p 50000:50000 --name jenkins jenkins/jenkins:lts
   ```

2. **Access Jenkins**: http://localhost:8080

3. **Add Credentials**:
   - ID: `registry-credentials`
   - Type: Username with password

4. **Create Pipeline**:
   - New Item → Pipeline
   - Pipeline script from SCM
   - Git repository URL
   - Script Path: `Jenkinsfile`

5. **Update Jenkinsfile**:
   - Set `REGISTRY = 'your-registry-url'`

6. **Build Now** → Monitor console

## ✅ Verification Checklist

- [ ] Application runs locally
- [ ] Tests pass
- [ ] Container builds successfully
- [ ] Container runs and responds to health check
- [ ] Web dashboard accessible
- [ ] API endpoints work
- [ ] Jenkins pipeline completes successfully
- [ ] Deployment log updated

## 📊 Sample Test Data

**High Credibility:**
```json
{
  "title": "Peer-Reviewed Study Confirms Climate Impact",
  "content": "Researchers from multiple institutions have verified the data through rigorous analysis with evidence.",
  "source": "Reuters"
}
```

**Low Credibility:**
```json
{
  "title": "SHOCKING SECRET Doctors Don't Want You to Know!",
  "content": "You won't believe this one weird trick! Act now!",
  "source": "Unknown"
}
```

## 🧹 Cleanup

```bash
# Remove containers
podman stop news-analyzer registry jenkins
podman rm news-analyzer registry jenkins

# Remove images
podman rmi news-credibility-analyzer:latest
podman rmi localhost:5000/news-credibility-analyzer:latest
```

