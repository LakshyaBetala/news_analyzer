# News Credibility Analyzer - Live Demonstration Guide

This guide provides step-by-step instructions for demonstrating the News Credibility Analyzer project in front of your professor/mam.

## Pre-Demo Checklist

- [ ] WSL is installed and running
- [ ] Python virtual environment is created and activated
- [ ] All dependencies are installed
- [ ] Application runs locally
- [ ] Container image is built
- [ ] Browser is ready (Chrome/Firefox)
- [ ] Terminal/command prompt is open
- [ ] Project files are accessible

## Demo Flow Overview

1. **Introduction** - Project overview and architecture
2. **Local Development** - Show code structure and run locally
3. **Testing** - Demonstrate test suite
4. **Containerization** - Build and run container
5. **Web Interface** - Live analysis demonstration
6. **API Testing** - Show REST API endpoints
7. **CI/CD Pipeline** - Jenkins pipeline (if configured)
8. **Versioning** - Show version tracking
9. **Q&A** - Answer questions

---

## Step-by-Step Demonstration

### Part 1: Introduction & Project Overview (2 minutes)

**What to Say:**
"Good morning/afternoon. Today I'll demonstrate the News Credibility Analyzer - a real-time web application that analyzes news articles for credibility using keyword-based scoring. The project includes complete CI/CD automation with Jenkins, containerization with Podman, and comprehensive testing."

**What to Show:**
```bash
# Open terminal in WSL
wsl

# Navigate to project
cd /mnt/c/Users/laksh/news-analyzer

# Show project structure
ls -la
tree -L 2  # if tree is installed, or use: find . -maxdepth 2 -type d
```

**Key Points to Mention:**
- Real-time credibility analysis
- Keyword-based scoring (extensible to transformers)
- Complete CI/CD pipeline
- Containerized deployment
- Automated versioning

---

### Part 2: Local Development Setup (3 minutes)

**What to Say:**
"Let me show you the local development setup. I've created a Python virtual environment to isolate dependencies."

**Commands to Run:**
```bash
# Show you're in WSL
pwd
uname -a

# Activate virtual environment
source venv/bin/activate

# Verify Python version
python --version

# Show installed packages
pip list

# Show project structure
ls -R app/
cat app/main.py | head -20
cat app/model.py | head -30
```

**What to Explain:**
- Virtual environment isolation
- Project structure (app/, tests/, etc.)
- Main application components (main.py, model.py)
- Flask framework for web API

---

### Part 3: Running Tests (2 minutes)

**What to Say:**
"The project includes comprehensive test coverage. Let me run the test suite."

**Commands to Run:**
```bash
# Make sure venv is activated
source venv/bin/activate

# Run tests with verbose output
pytest tests/ -v

# Show test coverage
pytest tests/ -v --cov=app --cov-report=term-missing
```

**What to Show:**
- All tests passing
- Test coverage report
- Different test scenarios (health, version, analysis, error handling)

**What to Explain:**
- Test coverage includes API endpoints
- Tests cover both success and error cases
- Tests verify credibility scoring logic

---

### Part 4: Running Application Locally (2 minutes)

**What to Say:**
"Now let me start the application locally to demonstrate it running."

**Commands to Run:**
```bash
# Activate venv
source venv/bin/activate

# Start application (in background or new terminal)
python -m app.main &

# Or run in foreground (Ctrl+C to stop later)
python -m app.main
```

**In New Terminal (or wait a moment):**
```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Test version endpoint
curl http://localhost:5000/api/version
```

**What to Show:**
- Application starts successfully
- Health check returns healthy status
- Version information is displayed

---

### Part 5: Containerization (3 minutes)

**What to Say:**
"The application is containerized using Podman for consistent deployment across environments."

**Commands to Run:**
```bash
# Stop local application if running
# (Ctrl+C or find and kill process)

# Show Dockerfile
cat Dockerfile

# Build container image
podman build -t news-credibility-analyzer:1.0.0 .

# Show image was created
podman images | grep news-credibility-analyzer

# Tag as latest
podman tag news-credibility-analyzer:1.0.0 news-credibility-analyzer:latest

# Run container
podman run -d \
  --name news-analyzer \
  -p 5000:5000 \
  -e APP_VERSION=1.0.0 \
  news-credibility-analyzer:1.0.0

# Verify container is running
podman ps

# Show container logs
podman logs news-analyzer
```

**What to Explain:**
- Dockerfile structure
- Multi-stage build (if applicable)
- Container health checks
- Environment variables
- Port mapping

---

### Part 6: Web Interface Demonstration (5 minutes)

**What to Say:**
"Now let me demonstrate the web interface. This is the main user-facing component."

**Steps:**
1. **Open Browser:**
   - Open Chrome/Firefox
   - Navigate to: http://localhost:5000

2. **Show Dashboard:**
   - Point out the clean, modern UI
   - Show version number displayed
   - Explain the form fields (title, content, source)

3. **Test Case 1: High Credibility Article**
   ```
   Title: Peer-Reviewed Study Confirms Climate Change Impact
   Content: Researchers from multiple institutions have verified the data through rigorous analysis. The study was published in a scientific journal after peer review. Evidence-based findings confirm the impact.
   Source: Reuters
   ```
   - Click "Analyze Credibility"
   - Show results:
     - High credibility score (>60)
     - Minimal risk factors
     - Positive recommendations

4. **Test Case 2: Low Credibility Article**
   ```
   Title: SHOCKING SECRET Doctors Don't Want You to Know!
   Content: You won't believe this one weird trick! Act now before it's too late! This miracle cure will change your life!
   Source: Unknown
   ```
   - Click "Analyze Credibility"
   - Show results:
     - Low credibility score (<40)
     - Multiple risk factors
     - Warnings and recommendations

5. **Test Case 3: Moderate Credibility**
   ```
   Title: Breaking News: Official Statement Released
   Content: An official statement was released today regarding the ongoing investigation.
   Source: (leave empty)
   ```
   - Show moderate score
   - Explain source evaluation

**What to Explain:**
- Real-time analysis
- Scoring algorithm (keyword-based)
- Risk factor identification
- Recommendation generation
- Visual feedback (score bar, color coding)

---

### Part 7: API Testing (3 minutes)

**What to Say:**
"The application also provides a REST API for programmatic access. Let me demonstrate the API endpoints."

**Commands to Run:**
```bash
# Health check
curl http://localhost:5000/api/health
echo ""

# Version endpoint
curl http://localhost:5000/api/version
echo ""

# Analyze endpoint - High credibility
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Research Study Confirms Findings",
    "content": "A peer-reviewed study published in a scientific journal provides evidence of climate change.",
    "source": "Reuters"
  }' | python -m json.tool

echo ""

# Analyze endpoint - Low credibility
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "title": "SHOCKING SECRET Doctors Dont Want You to Know!",
    "content": "You wont believe this one weird trick! Act now!",
    "source": "Unknown"
  }' | python -m json.tool
```

**What to Show:**
- JSON responses
- Credibility scores
- Risk factors
- Recommendations
- Timestamps
- Version information

**What to Explain:**
- RESTful API design
- JSON request/response format
- Error handling (show error case if time permits)

---

### Part 8: CI/CD Pipeline (3 minutes)

**What to Say:**
"The project includes a complete CI/CD pipeline using Jenkins for automated build, test, and deployment."

**What to Show:**
```bash
# Show Jenkinsfile
cat Jenkinsfile

# Explain pipeline stages
echo "Pipeline stages:"
echo "1. Checkout code"
echo "2. Run tests"
echo "3. Build container image"
echo "4. Tag image with version"
echo "5. Push to registry"
echo "6. Deploy container"
echo "7. Log deployment"
```

**If Jenkins is Set Up:**
- Open Jenkins in browser (http://localhost:8080)
- Show pipeline job
- Show build history
- Show deployment log:
  ```bash
  cat deployment_history.log
  ```

**What to Explain:**
- Automated testing
- Version tagging (BUILD_NUMBER.GIT_COMMIT)
- Container registry integration
- Automated deployment
- Deployment history tracking

---

### Part 9: Versioning & Deployment Log (2 minutes)

**What to Say:**
"The system includes automatic versioning and deployment tracking."

**Commands to Run:**
```bash
# Show version in API
curl http://localhost:5000/api/version

# Show deployment log
cat deployment_history.log

# Show container with version
podman inspect news-analyzer | grep -i version
```

**What to Explain:**
- Version format: BUILD_NUMBER.GIT_COMMIT_SHORT
- Version embedded in API responses
- Deployment history tracking
- Rollback capability

---

### Part 10: Code Structure & Extensibility (2 minutes)

**What to Say:**
"The architecture is designed for easy extension, particularly for adding transformer-based models."

**Commands to Run:**
```bash
# Show model.py structure
cat app/model.py | head -50

# Explain extensibility
echo "Key extensibility points:"
echo "- Modular analysis engine"
echo "- Plugin architecture for scoring methods"
echo "- Weighted combination of scores"
echo "- Easy integration of transformer models"
```

**What to Show:**
- Model architecture
- Keyword-based scoring logic
- Extension points documented in README

---

### Part 11: Project Documentation (1 minute)

**What to Say:**
"The project includes comprehensive documentation."

**What to Show:**
```bash
# List documentation files
ls -lh *.md

# Show README structure
head -30 README.md
```

**Key Documentation:**
- README.md - Full project documentation
- SETUP_GUIDE.md - Detailed setup instructions
- DEMO_REPORT.md - Project report text
- QUICK_START.md - Quick reference

---

### Part 12: Q&A Preparation

**Common Questions & Answers:**

**Q: How does the credibility scoring work?**
A: The system uses keyword-based heuristics to identify credible indicators (verified, fact-checked, peer-reviewed) and suspicious patterns (clickbait, emotional manipulation). It also evaluates source credibility and combines these factors into a 0-100 score.

**Q: Can this be extended with AI/ML models?**
A: Yes, the architecture is designed for easy extension. The model.py file can be updated to include transformer models (BERT, RoBERTa) alongside keyword scoring, with weighted combination of scores.

**Q: How does versioning work?**
A: Versions are automatically generated as BUILD_NUMBER.GIT_COMMIT_SHORT (e.g., 42.a1b2c3d). This is set during the Jenkins build, tagged in container images, and included in API responses.

**Q: What about production deployment?**
A: The containerized application can be deployed to any container orchestration platform (Kubernetes, Docker Swarm). The CI/CD pipeline automates the complete deployment process.

**Q: How do you handle errors?**
A: The API includes comprehensive error handling with appropriate HTTP status codes. The application includes health check endpoints for monitoring.

---

## Quick Reference Commands

### Start Demo
```bash
# Activate venv
source venv/bin/activate

# Start container
podman run -d -p 5000:5000 --name news-analyzer news-credibility-analyzer:latest

# Verify
curl http://localhost:5000/api/health
```

### During Demo
```bash
# Test API
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","content":"Test content","source":"Test"}'

# Check logs
podman logs news-analyzer

# Show version
curl http://localhost:5000/api/version
```

### End Demo
```bash
# Stop container
podman stop news-analyzer
podman rm news-analyzer
```

---

## Tips for Successful Demo

1. **Practice First**: Run through the entire demo at least once before presentation
2. **Have Backup**: Keep a pre-built container image ready
3. **Test Browser**: Ensure browser works with localhost:5000
4. **Prepare Examples**: Have article examples ready to copy-paste
5. **Time Management**: Allocate ~20-25 minutes total
6. **Be Confident**: Explain what you're doing as you do it
7. **Handle Errors**: If something fails, explain troubleshooting steps
8. **Show Enthusiasm**: Demonstrate passion for the project

---

## Troubleshooting During Demo

**If container won't start:**
```bash
podman logs news-analyzer
podman ps -a
```

**If port is in use:**
```bash
sudo lsof -i :5000
# Kill process or use different port
```

**If tests fail:**
```bash
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
pytest tests/ -v
```

**If API doesn't respond:**
```bash
# Check container status
podman ps

# Check logs
podman logs news-analyzer

# Restart container
podman restart news-analyzer
```

---

## Demo Checklist

Before starting:
- [ ] WSL is running
- [ ] Virtual environment is activated
- [ ] Container image is built
- [ ] Container is running
- [ ] Browser is open
- [ ] Terminal is ready
- [ ] Test articles are prepared
- [ ] Documentation is accessible

During demo:
- [ ] Show project structure
- [ ] Run tests successfully
- [ ] Demonstrate web interface
- [ ] Test API endpoints
- [ ] Show containerization
- [ ] Explain CI/CD pipeline
- [ ] Show versioning
- [ ] Answer questions confidently

---

**Good luck with your demonstration! 🚀**

