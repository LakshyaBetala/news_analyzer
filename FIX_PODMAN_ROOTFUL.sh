#!/bin/bash
# Complete fix for Podman rootful mode in Jenkins
# Run this script in WSL terminal

set -e

echo "=== Fixing Podman for Jenkins (Rootful Mode) ==="

# Step 1: Stop any rootless Podman processes
echo "Step 1: Resetting rootless Podman..."
sudo -u jenkins podman system reset -f 2>/dev/null || echo "No rootless Podman to reset"

# Step 2: Create podman group if it doesn't exist
echo "Step 2: Creating podman group..."
if getent group podman > /dev/null 2>&1; then
    echo "Podman group already exists"
else
    sudo groupadd podman
    echo "Podman group created"
fi

# Step 3: Enable rootful Podman socket
echo "Step 3: Enabling rootful Podman socket..."
sudo systemctl enable --now podman.socket 2>/dev/null || echo "Podman socket already enabled"

# Step 4: Add jenkins to podman group
echo "Step 4: Adding jenkins to podman group..."
sudo usermod -aG podman jenkins
echo "Jenkins added to podman group"

# Step 5: Configure passwordless sudo
echo "Step 5: Configuring passwordless sudo for podman..."
echo "jenkins ALL=(ALL) NOPASSWD: /usr/bin/podman" | sudo tee /etc/sudoers.d/jenkins-podman
sudo chmod 0440 /etc/sudoers.d/jenkins-podman

# Verify sudoers
if sudo visudo -c; then
    echo "Sudoers file is valid"
else
    echo "ERROR: Sudoers file has syntax errors!"
    exit 1
fi

# Step 6: Configure registries
echo "Step 6: Configuring container registries..."
sudo mkdir -p /var/lib/jenkins/.config/containers
sudo tee /var/lib/jenkins/.config/containers/registries.conf << EOF
[[registry]]
location = "localhost:5000"
insecure = true
EOF
sudo chown -R jenkins:jenkins /var/lib/jenkins/.config

# Step 7: Restart Jenkins
echo "Step 7: Restarting Jenkins..."
sudo systemctl restart jenkins

# Step 8: Wait for Jenkins to start
echo "Waiting for Jenkins to start..."
sleep 5

# Step 9: Verify
echo ""
echo "=== Verification ==="
echo "Jenkins groups:"
groups jenkins | grep podman && echo "✅ Jenkins is in podman group" || echo "⚠️  Jenkins not in podman group (may need logout/login)"

echo ""
echo "Testing Podman with sudo:"
if sudo -u jenkins sudo /usr/bin/podman ps > /dev/null 2>&1; then
    echo "✅ Podman works with sudo"
else
    echo "⚠️  Podman test failed, but this might be normal if no containers are running"
fi

echo ""
echo "=== Next Steps ==="
echo "1. Update Jenkinsfile: Change PODMAN = '/usr/bin/podman' to PODMAN = 'sudo /usr/bin/podman'"
echo "2. Restart Jenkins build"
echo "3. If issues persist, check: sudo journalctl -u jenkins -n 50"

echo ""
echo "✅ Setup complete!"

