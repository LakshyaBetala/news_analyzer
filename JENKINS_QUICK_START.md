# Jenkins Quick Start - Copy-Paste Commands

## Complete Installation (One Command Block)

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Java
sudo apt-get install -y openjdk-17-jdk

# Add Jenkins repository
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null

echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null

# Install Jenkins
sudo apt-get update
sudo apt-get install -y jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Get initial password
echo "=========================================="
echo "Jenkins Initial Admin Password:"
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
echo "=========================================="
echo ""
echo "Access Jenkins at: http://localhost:8080"
```

## Configure Podman Access

```bash
# Add jenkins user to podman group
sudo usermod -aG podman jenkins

# Configure local registry for jenkins
sudo mkdir -p /var/lib/jenkins/.config/containers
sudo tee /var/lib/jenkins/.config/containers/registries.conf << EOF
[[registry]]
location = "localhost:5000"
insecure = true
EOF

# Set ownership
sudo chown -R jenkins:jenkins /var/lib/jenkins/.config

# Restart Jenkins
sudo systemctl restart jenkins

# Verify Jenkins is running
sudo systemctl status jenkins
```

## Web UI Setup Steps

1. **Open:** http://localhost:8080
2. **Enter password:** (from command above)
3. **Install suggested plugins** (wait 5-10 minutes)
4. **Create admin user:**
   - Username: `admin`
   - Password: (choose strong password)
   - Email: (your email)
5. **Save and Finish**

## Create Pipeline Job

### Via Web UI:

1. Click **"New Item"**
2. Name: `news-analyzer-pipeline`
3. Select **"Pipeline"**
4. Click **"OK"**
5. **Pipeline Configuration:**
   - Definition: **"Pipeline script from SCM"**
   - SCM: **"Git"**
   - Repository URL: `file:///mnt/c/Users/laksh/news-analyzer`
   - Script Path: `Jenkinsfile`
6. Click **"Save"**
7. Click **"Build Now"**

### Verify Build:

```bash
# Check Jenkins logs
sudo journalctl -u jenkins -f

# Check if container was created
podman ps | grep news-analyzer

# Test deployed app
curl http://localhost:5000/api/health
```

## Troubleshooting Commands

```bash
# Check Jenkins status
sudo systemctl status jenkins

# View Jenkins logs
sudo journalctl -u jenkins -n 50

# Restart Jenkins
sudo systemctl restart jenkins

# Check if port 8080 is in use
sudo lsof -i :8080

# Verify Podman access
sudo -u jenkins podman --version

# Check Jenkins can see project
sudo -u jenkins ls -la /mnt/c/Users/laksh/news-analyzer
```

## Common Issues & Fixes

### Issue: "podman: command not found" in build

```bash
# Add Podman to Jenkins PATH
sudo systemctl edit jenkins

# Add this:
[Service]
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/bin"

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart jenkins
```

### Issue: Permission denied for Podman

```bash
# Fix permissions
sudo usermod -aG podman jenkins
sudo chmod 666 /var/run/podman.sock 2>/dev/null || true
sudo systemctl restart jenkins
```

### Issue: Cannot access project directory

```bash
# Give Jenkins read access
sudo chmod -R 755 /mnt/c/Users/laksh/news-analyzer
sudo chown -R $(whoami):jenkins /mnt/c/Users/laksh/news-analyzer
```

## Success Indicators

✅ Jenkins accessible at http://localhost:8080  
✅ Can log in with admin account  
✅ Pipeline job created and visible  
✅ Build starts when clicking "Build Now"  
✅ Build completes successfully  
✅ Container is deployed and running  
✅ Application responds at http://localhost:5000/api/health  

## Next Steps

1. ✅ Run first successful build
2. ✅ Set up automatic builds (polling or webhooks)
3. ✅ Configure email notifications
4. ✅ Add more pipeline stages
5. ✅ Set up build retention policies

---

**Need help?** Check `JENKINS_SETUP.md` for detailed instructions.

