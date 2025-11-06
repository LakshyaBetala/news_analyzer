# Fix Jenkins Git Branch Error

## Problem
Jenkins can't find the `main` branch. Error: `fatal: couldn't find remote ref refs/heads/main`

## Solution Options

### Option 1: Check Your Current Branch (Recommended)

Run these commands in WSL:

```bash
cd /mnt/c/Users/laksh/news-analyzer

# Check current branch
git branch

# Check all branches
git branch -a

# Check if it's a git repository
git status
```

**If you see `master` instead of `main`:**
- Your branch is `master`, not `main`
- Update Jenkins configuration (see below)

**If you see "not a git repository":**
- Initialize Git repo (see Option 2)

**If you see no branches:**
- Create initial commit (see Option 3)

### Option 2: Initialize Git Repository (If Not a Git Repo)

```bash
cd /mnt/c/Users/laksh/news-analyzer

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: News Credibility Analyzer"

# Create main branch (if on master)
git branch -M main

# Verify
git branch
```

### Option 3: Fix Jenkins Configuration

#### If Your Branch is `master` (not `main`):

1. **In Jenkins Web UI:**
   - Go to your pipeline: `news-analyzer-pipeline`
   - Click "Configure"
   - Scroll to "Pipeline" section
   - Under "Branches to build":
     - Change `*/main` to `*/master`
   - Click "Save"

#### If You Want to Use `main` Branch:

```bash
cd /mnt/c/Users/laksh/news-analyzer

# Check current branch
git branch

# If you're on master, rename to main
git branch -M main

# Or create main branch
git checkout -b main
git push -u origin main
```

### Option 4: Use Local File System (No Git Needed)

If you don't need Git, configure Jenkins to use the file system directly:

1. **In Jenkins Web UI:**
   - Go to pipeline: `news-analyzer-pipeline`
   - Click "Configure"
   - Scroll to "Pipeline" section
   - **Definition:** Select "Pipeline script"
   - **Script:** Copy the entire Jenkinsfile content
   - Click "Save"

**OR** use a different SCM approach:

1. **Definition:** "Pipeline script from SCM"
2. **SCM:** Select "None" (if available) or use a different method
3. **Script Path:** Leave empty, use inline script instead

### Option 5: Update Jenkinsfile to Handle Missing Branch

Update your Jenkinsfile to be more flexible:

```groovy
pipeline {
    agent any
    
    environment {
        REGISTRY = 'localhost:5000'
        IMAGE_NAME = 'news-credibility-analyzer'
        APP_VERSION = "${env.BUILD_NUMBER}.${env.GIT_COMMIT ? env.GIT_COMMIT.take(7) : 'local'}"
        DEPLOYMENT_LOG = 'deployment_history.log'
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "Checking out code..."
                    try {
                        checkout scm
                    } catch (Exception e) {
                        echo "Git checkout failed, using workspace directly"
                        sh 'pwd && ls -la'
                    }
                }
            }
        }
        
        // ... rest of stages
    }
}
```

## Quick Fix Commands

### Check and Fix Branch Name

```bash
# In WSL terminal
cd /mnt/c/Users/laksh/news-analyzer

# Check current branch
git branch

# If you see master, rename to main
git branch -M main

# Or if you want to keep master, update Jenkins config to use */master
```

### Initialize Git if Needed

```bash
cd /mnt/c/Users/laksh/news-analyzer

# Initialize if not a git repo
git init

# Add files
git add .

# Commit
git commit -m "Initial commit"

# Create/rename to main
git branch -M main

# Verify
git branch
git status
```

## Update Jenkins Configuration

### Method 1: Change Branch in Jenkins UI

1. Go to: http://localhost:8080
2. Click: `news-analyzer-pipeline`
3. Click: "Configure"
4. Find: "Branches to build" (under Pipeline → SCM)
5. Change: `*/main` to `*/master` (or your actual branch name)
6. Click: "Save"

### Method 2: Use Inline Script (No Git Required)

1. Go to: `news-analyzer-pipeline` → "Configure"
2. **Pipeline Definition:** Select "Pipeline script" (not "Pipeline script from SCM")
3. **Script:** Copy entire content from your `Jenkinsfile`
4. Click: "Save"

This way Jenkins uses the workspace directly without Git.

## Verify Fix

After making changes:

1. Click "Build Now" in Jenkins
2. Check "Console Output"
3. Should see: "Checking out code..." without errors
4. Build should proceed to "Test" stage

## Complete Setup (If Starting Fresh)

```bash
# In WSL
cd /mnt/c/Users/laksh/news-analyzer

# Initialize Git
git init
git add .
git commit -m "Initial commit: News Credibility Analyzer"

# Create main branch
git branch -M main

# Verify
git branch
git status
```

Then in Jenkins:
- Use branch: `*/main` or `master` (depending on what you have)
- Or use inline script method (no Git needed)

## Alternative: Use Different SCM Method

If Git continues to cause issues, you can:

1. **Use "Copy Artifacts" plugin:**
   - Copy files from another job
   - Or use file system directly

2. **Use "Pipeline script" directly:**
   - No SCM needed
   - Jenkinsfile content pasted directly
   - Works with local file system

3. **Use GitHub/GitLab:**
   - Push code to remote repository
   - Use HTTPS/SSH URL in Jenkins
   - More reliable than local file paths

## Recommended Solution

**For local development, use inline script:**

1. Jenkins → `news-analyzer-pipeline` → Configure
2. Pipeline → Definition: **"Pipeline script"**
3. Copy your entire Jenkinsfile content into the script box
4. Save

This avoids Git issues entirely and works directly with your local files.

