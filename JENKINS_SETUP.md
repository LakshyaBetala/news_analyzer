# Jenkins Setup Guide - From Scratch

Complete guide to install and configure Jenkins for the News Credibility Analyzer project.

## Prerequisites

- WSL2 installed and running
- Podman installed in WSL
- Git installed
- Project code available

---

## Part 1: Install Jenkins

### Option A: Install Jenkins in WSL (Recommended for Development)

```bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install Java (required for Jenkins)
sudo apt-get install -y openjdk-17-jdk

# Verify Java installation
java -version

# Add Jenkins repository
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null

echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null

# Update package list
sudo apt-get update

# Install Jenkins
sudo apt-get install -y jenkins

# Start Jenkins service
sudo systemctl start jenkins

# Enable Jenkins to start on boot
sudo systemctl enable jenkins

# Check Jenkins status
sudo systemctl status jenkins
```

### Option B: Run Jenkins in Podman Container (Alternative)

```bash
# Create directory for Jenkins data
mkdir -p ~/jenkins_home

# Run Jenkins container
podman run -d \
  --name jenkins \
  --restart=unless-stopped \
  -p 8080:8080 \
  -p 50000:50000 \
  -v ~/jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts

# View initial admin password
podman logs jenkins | grep -A 1 "Please use the following password"
```

**Note:** For this guide, we'll use Option A (WSL installation).

---

## Part 2: Initial Jenkins Setup

### Step 1: Access Jenkins Web Interface

1. **Open Jenkins in browser:**
   - From Windows: http://localhost:8080
   - From WSL: http://localhost:8080

2. **Get initial admin password:**
   ```bash
   sudo cat /var/lib/jenkins/secrets/initialAdminPassword
   ```
   Copy this password.

3. **Unlock Jenkins:**
   - Paste the password in the Jenkins web interface
   - Click "Continue"

### Step 2: Install Suggested Plugins

1. Click "Install suggested plugins"
2. Wait for installation to complete (5-10 minutes)
3. Create admin user:
   - Username: `admin` (or your choice)
   - Password: (choose a strong password)
   - Full name: `Jenkins Admin`
   - Email: (your email)
4. Click "Save and Continue"
5. Click "Save and Finish"
6. Click "Start using Jenkins"

---

## Part 3: Install Required Plugins

### Step 1: Access Plugin Manager

1. Click "Manage Jenkins" in the left sidebar
2. Click "Plugins"
3. Click "Available plugins" tab

### Step 2: Install Essential Plugins

Search and install these plugins (check the boxes, then click "Install without restart"):

**Core Plugins:**
- ✅ **Pipeline** (usually pre-installed)
- ✅ **Git** (usually pre-installed)
- ✅ **GitHub** (if using GitHub)
- ✅ **Docker Pipeline** (for Podman support)
- ✅ **Blue Ocean** (modern UI - optional but recommended)

**Additional Useful Plugins:**
- ✅ **HTML Publisher** (for test reports)
- ✅ **JUnit** (for test results)
- ✅ **Coverage** (for code coverage)
- ✅ **Credentials Binding** (for secure credentials)

### Step 3: Restart Jenkins

After installing plugins:
1. Check "Restart Jenkins when installation is complete"
2. Wait for restart (Jenkins will reload)

---

## Part 4: Configure Jenkins for Podman

### Step 1: Configure Podman Access

Jenkins needs to access Podman. Since Jenkins runs as `jenkins` user, we need to configure access:

```bash
# Add jenkins user to podman group (if using system Podman)
sudo usermod -aG podman jenkins

# Or if using rootless Podman, configure socket access
# Check Podman socket location
podman info | grep "runRoot"

# Restart Jenkins to apply changes
sudo systemctl restart jenkins
```

### Step 2: Test Podman Access from Jenkins

1. Go to Jenkins → Manage Jenkins → System Information
2. Look for environment variables
3. Verify Jenkins can see Podman (may need additional configuration)

**Alternative:** Use shell commands in Jenkinsfile (works without special config)

---

## Part 5: Configure Credentials

### Step 1: Access Credentials Manager

1. Click "Manage Jenkins"
2. Click "Credentials"
3. Click "System"
4. Click "Global credentials (unrestricted)"
5. Click "Add Credentials"

### Step 2: Add Registry Credentials (if using remote registry)

**For Docker Hub:**
- Kind: `Username with password`
- Scope: `Global`
- Username: `your-dockerhub-username`
- Password: `your-dockerhub-password`
- ID: `dockerhub-credentials`
- Description: `Docker Hub credentials`

**For Local Registry (if needed):**
- Usually not required for localhost:5000
- But if you set up authentication:
  - Kind: `Username with password`
  - ID: `registry-credentials`
  - Username: (your registry username)
  - Password: (your registry password)

### Step 3: Add Git Credentials (if using private repo)

**For GitHub:**
- Kind: `SSH Username with private key` or `Username with password`
- ID: `github-credentials`
- Username: `your-github-username`
- Password/Key: (your GitHub token or SSH key)

---

## Part 6: Create Jenkins Pipeline Job

### Step 1: Create New Pipeline

1. Click "New Item" on Jenkins dashboard
2. Enter item name: `news-analyzer-pipeline`
3. Select "Pipeline"
4. Click "OK"

### Step 2: Configure Pipeline

**General Settings:**
- ✅ Check "GitHub project" (if using GitHub)
  - Project url: `https://github.com/yourusername/news-analyzer`
- ✅ Check "Build Triggers" → "GitHub hook trigger for GITScm polling" (optional)

**Pipeline Configuration:**

1. **Definition:** Select "Pipeline script from SCM"
2. **SCM:** Select "Git"
3. **Repository URL:** 
   - If local: `file:///mnt/c/Users/laksh/news-analyzer`
   - If GitHub: `https://github.com/yourusername/news-analyzer.git`
4. **Credentials:** Select your Git credentials (if private repo)
5. **Branches to build:** `*/main` or `*/master`
6. **Script Path:** `Jenkinsfile`
7. **Lightweight checkout:** Uncheck this (we need full checkout)

### Step 3: Configure Environment Variables

Scroll down to "Pipeline" section and add environment variables if needed:

- `REGISTRY`: `localhost:5000` (or your registry URL)
- `IMAGE_NAME`: `news-credibility-analyzer`

### Step 4: Save Configuration

Click "Save"

---

## Part 7: Update Jenkinsfile for Your Environment

### Step 1: Check Current Jenkinsfile

```bash
cd /mnt/c/Users/laksh/news-analyzer
cat Jenkinsfile
```

### Step 2: Update Jenkinsfile if Needed

Make sure the `REGISTRY` variable matches your setup:

```groovy
environment {
    REGISTRY = 'localhost:5000'  // Change if using different registry
    IMAGE_NAME = 'news-credibility-analyzer'
}
```

### Step 3: Configure Registry for Jenkins

If using local registry, make sure Jenkins can access it:

```bash
# Configure Podman registries for jenkins user
sudo mkdir -p /var/lib/jenkins/.config/containers
sudo tee /var/lib/jenkins/.config/containers/registries.conf << EOF
[[registry]]
location = "localhost:5000"
insecure = true
EOF

# Set ownership
sudo chown -R jenkins:jenkins /var/lib/jenkins/.config
```

---

## Part 8: Run Your First Build

### Step 1: Trigger Build

1. Go to your pipeline: `news-analyzer-pipeline`
2. Click "Build Now"
3. Watch the build progress in "Build History"

### Step 2: View Build Logs

1. Click on the build number (#1)
2. Click "Console Output"
3. Watch the build progress

### Step 3: Troubleshoot Common Issues

**Issue: "podman: command not found"**
```bash
# Add Podman to Jenkins PATH
sudo nano /etc/systemd/system/jenkins.service

# Add to [Service] section:
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/bin"

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart jenkins
```

**Issue: "Permission denied" for Podman**
```bash
# Add jenkins to podman group
sudo usermod -aG podman jenkins
sudo systemctl restart jenkins
```

**Issue: "Cannot connect to registry"**
- Verify registry is running: `podman ps | grep registry`
- Check registries.conf is configured correctly
- Test from command line: `podman pull localhost:5000/news-credibility-analyzer:1.0.0`

---

## Part 9: Configure Build Triggers (Optional)

### Option 1: Poll SCM

1. In pipeline configuration, check "Poll SCM"
2. Schedule: `H/5 * * * *` (every 5 minutes)
3. This checks for code changes and builds automatically

### Option 2: GitHub Webhook

1. In GitHub repo → Settings → Webhooks
2. Add webhook:
   - Payload URL: `http://your-jenkins-url:8080/github-webhook/`
   - Content type: `application/json`
   - Events: `Just the push event`
3. Save webhook

### Option 3: Manual Build

Just click "Build Now" when you want to build.

---

## Part 10: View Build Results

### Step 1: Access Build Dashboard

1. Click on your pipeline
2. Click on a build number
3. View:
   - **Console Output:** Full build log
   - **Changes:** Git commits
   - **Test Result:** Test reports (if configured)
   - **Coverage Report:** Code coverage (if configured)

### Step 2: View Deployment Log

```bash
# Check deployment history
cat /mnt/c/Users/laksh/news-analyzer/deployment_history.log
```

---

## Part 11: Advanced Configuration

### Configure Email Notifications

1. Manage Jenkins → Configure System
2. Scroll to "E-mail Notification"
3. Configure SMTP server
4. Test email configuration

### Configure Build Parameters

1. In pipeline config, check "This project is parameterized"
2. Add parameters:
   - `APP_VERSION` (String parameter)
   - `DEPLOY_ENV` (Choice: dev, staging, prod)

### Set Up Build Retention

1. In pipeline config → "Build History"
2. Set "Days to keep builds": `30`
3. Set "Max # of builds to keep": `50`

---

## Part 12: Quick Reference Commands

### Jenkins Service Management

```bash
# Start Jenkins
sudo systemctl start jenkins

# Stop Jenkins
sudo systemctl stop jenkins

# Restart Jenkins
sudo systemctl restart jenkins

# Check status
sudo systemctl status jenkins

# View logs
sudo journalctl -u jenkins -f
```

### Access Jenkins

- Web UI: http://localhost:8080
- Default user: `admin` (or the one you created)
- Password: (the one you set during setup)

### Reset Admin Password (if forgotten)

```bash
# Stop Jenkins
sudo systemctl stop jenkins

# Edit config
sudo nano /var/lib/jenkins/config.xml

# Find <useSecurity>true</useSecurity> and change to false

# Start Jenkins
sudo systemctl start jenkins

# Access Jenkins, disable security, set new password
# Then re-enable security
```

---

## Part 13: Verification Checklist

After setup, verify:

- [ ] Jenkins is accessible at http://localhost:8080
- [ ] Can log in with admin account
- [ ] All required plugins are installed
- [ ] Pipeline job is created
- [ ] Jenkinsfile is detected
- [ ] Build can start (even if it fails)
- [ ] Podman commands work in build
- [ ] Registry is accessible
- [ ] Container can be built
- [ ] Container can be deployed

---

## Troubleshooting

### Jenkins won't start

```bash
# Check logs
sudo journalctl -u jenkins -n 50

# Check Java
java -version

# Check port 8080
sudo lsof -i :8080

# Restart service
sudo systemctl restart jenkins
```

### Build fails immediately

- Check Jenkinsfile syntax
- Verify Git repository is accessible
- Check console output for specific errors

### Podman not found in build

- Add Podman to PATH in Jenkins service
- Or use full path: `/usr/bin/podman`

### Permission issues

```bash
# Fix Jenkins home permissions
sudo chown -R jenkins:jenkins /var/lib/jenkins

# Add jenkins to required groups
sudo usermod -aG podman,docker jenkins
sudo systemctl restart jenkins
```

---

## Next Steps

1. ✅ Run your first successful build
2. ✅ Verify container is deployed
3. ✅ Test the deployed application
4. ✅ Set up automatic builds (polling or webhooks)
5. ✅ Configure notifications
6. ✅ Add more pipeline stages (testing, security scanning, etc.)

---

## Quick Start Summary

```bash
# 1. Install Jenkins
sudo apt-get update
sudo apt-get install -y openjdk-17-jdk
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update
sudo apt-get install -y jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# 2. Get initial password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword

# 3. Access http://localhost:8080 and complete setup

# 4. Configure Podman access
sudo usermod -aG podman jenkins
sudo mkdir -p /var/lib/jenkins/.config/containers
sudo tee /var/lib/jenkins/.config/containers/registries.conf << EOF
[[registry]]
location = "localhost:5000"
insecure = true
EOF
sudo chown -R jenkins:jenkins /var/lib/jenkins/.config
sudo systemctl restart jenkins

# 5. Create pipeline job in Jenkins web UI
# 6. Run first build!
```

Good luck! 🚀

