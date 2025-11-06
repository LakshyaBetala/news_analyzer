# News Credibility Analyzer - Complete Setup & Demo Guide (WSL)

## Prerequisites

- Windows 10/11 with WSL2 installed
- Python 3.11+ (in WSL)
- Podman (or Docker) installed in WSL
- Jenkins (for CI/CD) - optional
- Git installed in WSL

## WSL Setup (If Not Already Done)

### Check WSL Installation
```bash
wsl --version
```

### Install WSL2 (if needed)
```powershell
# Run in PowerShell (as Administrator)
wsl --install
```

### Access WSL
```bash
# Open WSL terminal or run:
wsl
```

### Navigate to Project Directory
```bash
# If project is in Windows filesystem
cd /mnt/c/Users/laksh/news-analyzer

# Or if project is in WSL filesystem
cd ~/news-analyzer
```

## 1. Local Development Setup

### Step 1: Update System Packages
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Step 2: Install Python and pip (if not installed)
```bash
sudo apt-get install -y python3 python3-pip python3-venv
```

### Step 3: Verify Python Installation
```bash
python3 --version
pip3 --version
```

### Step 4: Create Python Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (prompt should show (venv))
which python
```

### Step 5: Upgrade pip
```bash
pip install --upgrade pip
```

### Step 6: Install Dependencies
```bash
# Make sure you're in the project directory and venv is activated
pip install -r requirements.txt
```

### Step 7: Verify Installation
```bash
pip list
```

### Step 8: Run Application Locally
```bash
# Make sure you're in the project root directory
cd /mnt/c/Users/laksh/news-analyzer

# Make sure venv is activated
source venv/bin/activate

# Run application (from project root)
python -m app.main

# Or alternatively (also from project root):
python app/main.py
```

**Important:** Always run from the project root directory (`/mnt/c/Users/laksh/news-analyzer`), not from inside the `app/` directory.

### Step 9: Run Tests
```bash
# Activate venv if not already activated
source venv/bin/activate

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Step 10: Access Dashboard
Open browser on Windows: http://localhost:5000

**Note:** WSL2 allows direct access to localhost from Windows browser.

### Deactivate Virtual Environment (when done)
```bash
deactivate
```

## 2. Install Podman in WSL (If Not Installed)

### Install Podman
```bash
# Add Podman repository
. /etc/os-release
echo "deb https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${VERSION_ID}/ /" | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list
curl -L "https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${VERSION_ID}/Release.key" | sudo apt-key add -
sudo apt-get update

# Install Podman
sudo apt-get install -y podman

# Verify installation
podman --version
```

### Alternative: Install Docker (if preferred)
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker

# Verify installation
docker --version
```

## 3. Podman Image Build & Run

### Build Image
```bash
# Make sure you're in the project directory
cd /mnt/c/Users/laksh/news-analyzer

# Build image
podman build -t news-credibility-analyzer:1.0.0 .

# Or if using Docker:
docker build -t news-credibility-analyzer:1.0.0 .
```

### Tag Image
```bash
podman tag news-credibility-analyzer:1.0.0 news-credibility-analyzer:latest

# Or with Docker:
docker tag news-credibility-analyzer:1.0.0 news-credibility-analyzer:latest
```

### Run Container
```bash
podman run -d \
  --name news-analyzer \
  -p 5000:5000 \
  -e APP_VERSION=1.0.0 \
  news-credibility-analyzer:1.0.0

# Or with Docker:
docker run -d \
  --name news-analyzer \
  -p 5000:5000 \
  -e APP_VERSION=1.0.0 \
  news-credibility-analyzer:1.0.0
```

### Check Container Status
```bash
# List running containers
podman ps

# View container logs
podman logs news-analyzer

# Or with Docker:
docker ps
docker logs news-analyzer
```

### Test Health Endpoint
```bash
# Test from WSL
curl http://localhost:5000/api/health

# Or test from Windows PowerShell:
curl http://localhost:5000/api/health
```

### Stop Container
```bash
podman stop news-analyzer
podman rm news-analyzer

# Or with Docker:
docker stop news-analyzer
docker rm news-analyzer
```

## 4. Local Registry Setup (Optional)

### Step 1: Check if Port 5000 is Available
```bash
# Check what's using port 5000
sudo lsof -i :5000
# or
sudo netstat -tulpn | grep 5000

# If port 5000 is in use, stop the service or use a different port
# Option 1: Stop existing service (if it's your app)
podman stop news-analyzer 2>/dev/null || true

# Option 2: Use different port for registry (e.g., 5001)
# REGISTRY_PORT=5001
```

### Step 2: Configure Podman for Insecure Local Registry

**Important:** Podman requires configuration to use HTTP (not HTTPS) for local registries.

```bash
# Create registries configuration directory if it doesn't exist
mkdir -p ~/.config/containers

# Add localhost:5000 to insecure registries
cat >> ~/.config/containers/registries.conf << EOF
[[registry]]
location = "localhost:5000"
insecure = true
EOF

# Verify configuration
cat ~/.config/containers/registries.conf
```

**Alternative:** If the above doesn't work, edit the system-wide config:
```bash
# Edit system registries config (requires sudo)
sudo nano /etc/containers/registries.conf

# Add this section:
# [[registry]]
# location = "localhost:5000"
# insecure = true
```

### Step 3: Start Local Registry

**Option A: Use Port 5000 (if available)**
```bash
# Start registry on port 5000
podman run -d -p 5000:5000 --name registry docker.io/library/registry:2

# Verify registry is running
curl http://localhost:5000/v2/
# Should return: {}
```

**Option B: Use Different Port (if 5000 is in use)**
```bash
# Start registry on port 5001
podman run -d -p 5001:5000 --name registry docker.io/library/registry:2

# Update registries.conf to use port 5001
cat >> ~/.config/containers/registries.conf << EOF
[[registry]]
location = "localhost:5001"
insecure = true
EOF
```

### Step 4: Build and Push to Local Registry

**If using port 5000:**
```bash
# Build image
podman build -t localhost:5000/news-credibility-analyzer:1.0.0 .

# Tag as latest
podman tag localhost:5000/news-credibility-analyzer:1.0.0 localhost:5000/news-credibility-analyzer:latest

# Push to registry
podman push localhost:5000/news-credibility-analyzer:1.0.0
podman push localhost:5000/news-credibility-analyzer:latest
```

**If using port 5001:**
```bash
# Build image
podman build -t localhost:5001/news-credibility-analyzer:1.0.0 .

# Tag as latest
podman tag localhost:5001/news-credibility-analyzer:1.0.0 localhost:5001/news-credibility-analyzer:latest

# Push to registry
podman push localhost:5001/news-credibility-analyzer:1.0.0
podman push localhost:5001/news-credibility-analyzer:latest
```

### Step 5: Pull and Run from Registry

**If using port 5000:**
```bash
# Pull from registry
podman pull localhost:5000/news-credibility-analyzer:1.0.0

# Run container (use different port for app, e.g., 5001)
podman run -d -p 5001:5000 --name news-analyzer localhost:5000/news-credibility-analyzer:1.0.0

# Test
curl http://localhost:5001/api/health
```

**If using port 5001 for registry:**
```bash
# Pull from registry
podman pull localhost:5001/news-credibility-analyzer:1.0.0

# Run container on port 5000
podman run -d -p 5000:5000 --name news-analyzer localhost:5001/news-credibility-analyzer:1.0.0

# Test
curl http://localhost:5000/api/health
```

### Troubleshooting Registry Issues

**If you get TLS certificate errors:**
```bash
# Verify registries.conf is correct
cat ~/.config/containers/registries.conf

# Restart Podman service (if using systemd)
systemctl --user restart podman.socket

# Or restart WSL
wsl --shutdown
# Then restart WSL
```

**If port is still in use:**
```bash
# Find and kill process using port 5000
sudo lsof -i :5000
sudo kill -9 <PID>

# Or use a different port for registry
podman stop registry
podman rm registry
podman run -d -p 5001:5000 --name registry docker.io/library/registry:2
```

## 5. Jenkins CI/CD Setup

### Jenkins Installation (if needed)
```bash
# On Linux
sudo apt-get update
sudo apt-get install jenkins

# Or use Docker/Podman
podman run -d -p 8080:8080 -p 50000:50000 --name jenkins jenkins/jenkins:lts
```

### Jenkins Configuration Steps

1. **Access Jenkins:**
   - Open http://localhost:8080
   - Get initial admin password: `podman exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword`

2. **Install Required Plugins:**
   - Pipeline
   - Git
   - Docker Pipeline (optional)

3. **Configure Credentials:**
   - Jenkins → Manage Jenkins → Credentials
   - Add credentials with ID: `registry-credentials`
   - Type: Username with password
   - Username: your-registry-user
   - Password: your-registry-password

4. **Create Pipeline Job:**
   - New Item → Pipeline
   - Name: `news-analyzer-pipeline`
   - Pipeline → Definition: Pipeline script from SCM
   - SCM: Git
   - Repository URL: your-repo-url
   - Script Path: Jenkinsfile

5. **Configure Jenkinsfile REGISTRY:**
   - Edit Jenkinsfile
   - Update `REGISTRY = 'your-registry-url'` (e.g., `localhost:5000` or `registry.example.com`)

6. **Run Pipeline:**
   - Click "Build Now"
   - Monitor in Console Output

## 6. CI/CD Pipeline Flow

The Jenkins pipeline executes:

1. **Checkout** → Get code from Git
2. **Test** → Run pytest with coverage
3. **Build Image** → Build Podman image with version tag
4. **Tag Image** → Tag with version and latest
5. **Push to Registry** → Push to container registry
6. **Deploy** → Stop old container, start new one
7. **Log Deployment** → Write to deployment_history.log

### Version Format
`{BUILD_NUMBER}.{GIT_COMMIT_SHORT}`
- Example: `42.a1b2c3d`

## 7. Demo & Verification Steps

### Step 1: Verify Application Runs
```bash
# Start container
podman run -d -p 5000:5000 --name news-analyzer news-credibility-analyzer:latest

# Check health
curl http://localhost:5000/api/health

# Expected response:
# {"status":"healthy","version":"1.0.0","timestamp":"2025-06-11T22:00:00Z"}
```

### Step 2: Test API Endpoint
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Research Study Confirms Climate Change Impact",
    "content": "A peer-reviewed study published in a scientific journal provides evidence of climate change.",
    "source": "Reuters"
  }'
```

### Step 3: Access Web Dashboard
- Open http://localhost:5000
- Enter article title and content
- Click "Analyze Credibility"
- Verify score, risk factors, and recommendations display

### Step 4: Verify Versioning
```bash
curl http://localhost:5000/api/version

# Expected: {"version":"1.0.0","service":"news-credibility-analyzer"}
```

### Step 5: Check Deployment Log
```bash
cat deployment_history.log
```

### Step 6: Run Tests
```bash
pytest tests/ -v

# Expected: All tests pass
```

## 8. Sample Test Cases

### High Credibility Article
```json
{
  "title": "Peer-Reviewed Study Confirms Findings",
  "content": "Researchers from multiple institutions have verified the data through rigorous analysis.",
  "source": "Reuters"
}
```
Expected: High credibility score (>60)

### Low Credibility Article
```json
{
  "title": "SHOCKING SECRET Doctors Don't Want You to Know!",
  "content": "You won't believe this one weird trick! Act now before it's too late!",
  "source": "Unknown"
}
```
Expected: Low credibility score (<40)

## 9. Troubleshooting

### Container won't start
```bash
# Check logs
podman logs news-analyzer

# Check if port is in use
sudo lsof -i :5000
# or
sudo netstat -tulpn | grep 5000
```

### Jenkins pipeline fails
- Check Podman is accessible: `podman --version`
- Verify registry credentials
- Check Jenkins console for specific errors
- Ensure Git repository is accessible

### Tests fail
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Run tests
pytest tests/ -v
```

### Port Already in Use
```bash
# Find process using port 5000
sudo lsof -i :5000
# or
sudo netstat -tulpn | grep 5000

# Kill the process
sudo kill -9 <PID>
```

### WSL Network Issues
```bash
# Restart WSL network
sudo service networking restart

# Or restart WSL from PowerShell:
wsl --shutdown
# Then restart WSL
```

## 10. Cleanup Commands

```bash
# Stop and remove container
podman stop news-analyzer
podman rm news-analyzer

# Remove images
podman rmi news-credibility-analyzer:latest
podman rmi news-credibility-analyzer:1.0.0

# Clean up registry (if local)
podman stop registry
podman rm registry
```

## 11. Production Deployment Notes

- Use proper container registry (Docker Hub, Quay.io, etc.)
- Set up proper authentication
- Use secrets management for credentials
- Configure reverse proxy (nginx, traefik)
- Set up monitoring and logging
- Use orchestration (Kubernetes, Podman Compose)
- Enable HTTPS/TLS

