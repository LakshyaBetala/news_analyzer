# Local Registry Setup Guide - Quick Fix

## Problem: TLS Certificate Error

When you see this error:
```
Error: tls: failed to verify certificate: x509: certificate relies on legacy Common Name field
```

This means Podman is trying to use HTTPS for your local registry, but the registry only supports HTTP.

## Solution: Configure Podman for Insecure Registry

### Step 1: Create/Edit Registries Configuration

```bash
# Create config directory
mkdir -p ~/.config/containers

# Add localhost:5000 as insecure registry
cat > ~/.config/containers/registries.conf << EOF
[[registry]]
location = "localhost:5000"
insecure = true
EOF
```

### Step 2: Verify Configuration

```bash
cat ~/.config/containers/registries.conf
```

Should show:
```
[[registry]]
location = "localhost:5000"
insecure = true
```

### Step 3: Restart Podman (if needed)

```bash
# Restart Podman socket
systemctl --user restart podman.socket 2>/dev/null || true

# Or just restart WSL
wsl --shutdown
# Then restart WSL terminal
```

## Problem: Port 5000 Already in Use

### Solution 1: Stop Existing Service

```bash
# Check what's using port 5000
sudo lsof -i :5000

# Stop your application if it's running
podman stop news-analyzer
podman rm news-analyzer

# Or kill the process
sudo kill -9 <PID>
```

### Solution 2: Use Different Port for Registry

```bash
# Stop existing registry
podman stop registry 2>/dev/null || true
podman rm registry 2>/dev/null || true

# Start registry on port 5001
podman run -d -p 5001:5000 --name registry docker.io/library/registry:2

# Update registries.conf
cat > ~/.config/containers/registries.conf << EOF
[[registry]]
location = "localhost:5001"
insecure = true
EOF

# Now use localhost:5001 instead of localhost:5000
podman build -t localhost:5001/news-credibility-analyzer:1.0.0 .
podman push localhost:5001/news-credibility-analyzer:1.0.0
```

## Complete Working Example

```bash
# 1. Configure insecure registry
mkdir -p ~/.config/containers
cat > ~/.config/containers/registries.conf << EOF
[[registry]]
location = "localhost:5000"
insecure = true
EOF

# 2. Stop anything using port 5000
podman stop news-analyzer registry 2>/dev/null || true
podman rm news-analyzer registry 2>/dev/null || true

# 3. Start registry
podman run -d -p 5000:5000 --name registry docker.io/library/registry:2

# 4. Verify registry is running
curl http://localhost:5000/v2/
# Should return: {}

# 5. Build and tag image
podman build -t localhost:5000/news-credibility-analyzer:1.0.0 .
podman tag localhost:5000/news-credibility-analyzer:1.0.0 localhost:5000/news-credibility-analyzer:latest

# 6. Push to registry
podman push localhost:5000/news-credibility-analyzer:1.0.0
podman push localhost:5000/news-credibility-analyzer:latest

# 7. Pull and run
podman pull localhost:5000/news-credibility-analyzer:1.0.0
podman run -d -p 5001:5000 --name news-analyzer localhost:5000/news-credibility-analyzer:1.0.0

# 8. Test
curl http://localhost:5001/api/health
```

## Alternative: Skip Registry, Use Local Images

If you don't need a registry, you can just use local images:

```bash
# Build locally
podman build -t news-credibility-analyzer:1.0.0 .

# Run directly
podman run -d -p 5000:5000 --name news-analyzer news-credibility-analyzer:1.0.0

# Test
curl http://localhost:5000/api/health
```

No registry needed!

