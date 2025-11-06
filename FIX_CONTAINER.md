# Fix Container Issues - Quick Guide

## Problem: Wrong Container Running or Port Conflict

### Step 1: Check What's Running

```bash
# List all running containers
podman ps -a

# Check what's using port 5001
sudo lsof -i :5001
# or
sudo netstat -tulpn | grep 5001
```

### Step 2: Stop All Related Containers

```bash
# Stop and remove all news-analyzer containers
podman stop news-analyzer 2>/dev/null || true
podman rm news-analyzer 2>/dev/null || true

# Stop anything on port 5001
podman ps --format "{{.Names}}\t{{.Ports}}" | grep 5001
# Then stop those containers
```

### Step 3: Verify Your Image Exists

```bash
# List all images
podman images | grep news-credibility-analyzer

# If image doesn't exist, build it
podman build -t news-credibility-analyzer:1.0.0 .
```

### Step 4: Run the Correct Container

```bash
# Option 1: Run from local image (no registry needed)
podman run -d \
  --name news-analyzer \
  --replace \
  -p 5000:5000 \
  -e APP_VERSION=1.0.0 \
  news-credibility-analyzer:1.0.0

# Option 2: If you want to use port 5001 (and registry image exists)
podman run -d \
  --name news-analyzer \
  --replace \
  -p 5001:5000 \
  -e APP_VERSION=1.0.0 \
  localhost:5000/news-credibility-analyzer:1.0.0
```

### Step 5: Verify It's Working

```bash
# Check container is running
podman ps

# Check logs
podman logs news-analyzer

# Test health endpoint
curl http://localhost:5000/api/health
# or if using port 5001:
curl http://localhost:5001/api/health

# Test version endpoint
curl http://localhost:5000/api/version
```

## Complete Clean Start

```bash
# 1. Stop everything
podman stop $(podman ps -q) 2>/dev/null || true
podman rm news-analyzer 2>/dev/null || true

# 2. Build fresh image
podman build -t news-credibility-analyzer:1.0.0 .

# 3. Run container
podman run -d \
  --name news-analyzer \
  --replace \
  -p 5000:5000 \
  -e APP_VERSION=1.0.0 \
  news-credibility-analyzer:1.0.0

# 4. Wait a moment for startup
sleep 3

# 5. Test
curl http://localhost:5000/api/health
curl http://localhost:5000/api/version

# 6. Open in browser
# http://localhost:5000
```

## Troubleshooting

### If you see "Hello from Flask via Podman!!!"

This means you're running a different container. Make sure you:
1. Built the correct image from your project
2. Are using the correct image name
3. Stopped the old container first

### If port is still in use

```bash
# Find process
sudo lsof -i :5001

# Kill it
sudo kill -9 <PID>

# Or use different port
podman run -d -p 5002:5000 --name news-analyzer news-credibility-analyzer:1.0.0
```

### If container exits immediately

```bash
# Check logs
podman logs news-analyzer

# Run interactively to see errors
podman run -it --rm -p 5000:5000 news-credibility-analyzer:1.0.0
```

