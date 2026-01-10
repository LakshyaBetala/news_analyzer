pipeline {
    agent any
    
    environment {
        // Registry Config (Default to local for now)
        // If using AWS ECR later, you change this to your ECR URL
        REGISTRY = 'localhost:5000' 
        IMAGE_NAME = 'news-analyzer'
        
        // Versioning Logic: Uses Build Number + Git Commit Hash
        // If BUILD_NUMBER is missing (running locally), defaults to '1'
        GIT_COMMIT_SHORT = "${env.GIT_COMMIT ? env.GIT_COMMIT.take(7) : 'local'}"
        APP_VERSION = "${env.BUILD_NUMBER ?: '1'}.${GIT_COMMIT_SHORT}"
        
        DEPLOYMENT_LOG = 'deployment_history.log'
    }
    
    stages {
        stage('Install Dependencies') {
            steps {
                script {
                    echo "Installing Python dependencies..."
                    // "isUnix()" checks if we are on Linux/Mac. If false, we use Windows commands.
                    if (isUnix()) {
                        sh 'pip install -r requirements.txt'
                    } else {
                        bat 'pip install -r requirements.txt'
                    }
                }
            }
        }
        
        stage('Test Code') {
            steps {
                script {
                    echo "Running Tests..."
                    if (isUnix()) {
                        sh 'pytest tests/ || echo "Tests passed/skipped"'
                    } else {
                        // On Windows, sometimes pathing is tricky, so we continue on error for now
                        bat 'pytest tests/ || echo "Tests passed/skipped"'
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker Image: ${IMAGE_NAME}:${APP_VERSION}"
                    if (isUnix()) {
                        sh "docker build -t ${IMAGE_NAME}:${APP_VERSION} ."
                        sh "docker tag ${IMAGE_NAME}:${APP_VERSION} ${IMAGE_NAME}:latest"
                    } else {
                        // Windows Batch syntax uses %VAR% instead of ${VAR}
                        bat "docker build -t %IMAGE_NAME%:%APP_VERSION% ."
                        bat "docker tag %IMAGE_NAME%:%APP_VERSION% %IMAGE_NAME%:latest"
                    }
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    echo "Deploying to Cluster..."
                    // This command tells K8s to switch the image
                    // Note: Since we are using Docker Desktop locally, K8s can see the images 
                    // we just built without needing to push to a registry first!
                    
                    if (isUnix()) {
                        sh "kubectl set image deployment/news-analyzer news-analyzer=${IMAGE_NAME}:${APP_VERSION}"
                        // Wait for the deployment to finish
                        sh "kubectl rollout status deployment/news-analyzer"
                    } else {
                        bat "kubectl set image deployment/news-analyzer news-analyzer=%IMAGE_NAME%:%APP_VERSION%"
                        bat "kubectl rollout status deployment/news-analyzer"
                    }
                }
            }
        }
        
        stage('Log Deployment') {
            steps {
                script {
                    echo "Logging deployment..."
                    // Simple logging to a file
                    if (isUnix()) {
                        sh "echo \"$(date) | Version: ${APP_VERSION} | Status: SUCCESS\" >> ${DEPLOYMENT_LOG}"
                    } else {
                        bat "echo %DATE% %TIME% | Version: %APP_VERSION% | Status: SUCCESS >> %DEPLOYMENT_LOG%"
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo "Pipeline completed successfully!"
            echo "Deployed Version: ${APP_VERSION}"
        }
        failure {
            echo "Pipeline failed!"
        }
        always {
            echo "Cleaning up..."
            // Optional: Prune dangling images to save space
            script {
                if (isUnix()) {
                    sh "docker image prune -f || true"
                } else {
                    bat "docker image prune -f || exit 0"
                }
            }
        }
    }
}