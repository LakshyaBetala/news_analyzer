pipeline {
    agent any
    
    environment {
        // Registry configuration - adjust for your setup
        REGISTRY = 'localhost:5000'  // Local registry or change to your registry
        IMAGE_NAME = 'news-credibility-analyzer'
        // Handle Git commit - use BUILD_NUMBER if Git not available
        GIT_COMMIT_SHORT = "${env.GIT_COMMIT ? env.GIT_COMMIT.take(7) : 'local'}"
        APP_VERSION = "${env.BUILD_NUMBER}.${GIT_COMMIT_SHORT}"
        DEPLOYMENT_LOG = 'deployment_history.log'
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "Checking out code..."
                    try {
                        checkout scm
                        echo "Git checkout successful"
                    } catch (Exception e) {
                        echo "Git checkout failed or not configured, using workspace directly"
                        echo "Error: ${e.getMessage()}"
                        sh 'pwd && ls -la'
                    }
                }
            }
        }
        
        stage('Test') {
        steps {
            script {
                echo "Running tests..."
                sh '''
                python3 -m pytest tests/ -v --cov=app --cov-report=term-missing
                '''
                }
            }
        }
        
        stage('Build Image') {
            steps {
                script {
                    echo "Building Podman image..."
                    sh """
                        podman build -t ${IMAGE_NAME}:${APP_VERSION} .
                        podman tag ${IMAGE_NAME}:${APP_VERSION} ${IMAGE_NAME}:latest
                    """
                }
            }
        }
        
        stage('Tag Image') {
            steps {
                script {
                    echo "Tagging image for registry..."
                    sh """
                        podman tag ${IMAGE_NAME}:${APP_VERSION} ${REGISTRY}/${IMAGE_NAME}:${APP_VERSION}
                        podman tag ${IMAGE_NAME}:latest ${REGISTRY}/${IMAGE_NAME}:latest
                    """
                }
            }
        }
        
        stage('Push to Registry') {
            steps {
                script {
                    echo "Pushing image to registry..."
                    // For local registry, credentials are usually not needed
                    // For remote registries, uncomment the withCredentials block
                    if (REGISTRY.contains('localhost') || REGISTRY.contains('127.0.0.1')) {
                        // Local registry - no authentication needed
                        sh """
                            podman push ${REGISTRY}/${IMAGE_NAME}:${APP_VERSION}
                            podman push ${REGISTRY}/${IMAGE_NAME}:latest
                        """
                    } else {
                        // Remote registry - use credentials
                        withCredentials([usernamePassword(
                            credentialsId: 'registry-credentials',
                            usernameVariable: 'REGISTRY_USER',
                            passwordVariable: 'REGISTRY_PASS'
                        )]) {
                            sh """
                                echo \$REGISTRY_PASS | podman login ${REGISTRY} -u \$REGISTRY_USER --password-stdin
                                podman push ${REGISTRY}/${IMAGE_NAME}:${APP_VERSION}
                                podman push ${REGISTRY}/${IMAGE_NAME}:latest
                            """
                        }
                    }
                }
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    echo "Deploying application..."
                    sh """
                        # Stop existing container if running
                        podman stop ${IMAGE_NAME} || true
                        podman rm ${IMAGE_NAME} || true
                        
                        # Run new container
                        # Use registry image if available, otherwise use local image
                        if podman image exists ${REGISTRY}/${IMAGE_NAME}:${APP_VERSION}; then
                            podman run -d \\
                                --name ${IMAGE_NAME} \\
                                -p 5000:5000 \\
                                -e APP_VERSION=${APP_VERSION} \\
                                ${REGISTRY}/${IMAGE_NAME}:${APP_VERSION}
                        else
                            podman run -d \\
                                --name ${IMAGE_NAME} \\
                                -p 5000:5000 \\
                                -e APP_VERSION=${APP_VERSION} \\
                                ${IMAGE_NAME}:${APP_VERSION}
                        fi
                        
                        # Wait for health check
                        sleep 5
                        
                        # Verify deployment
                        curl -f http://localhost:5000/api/health || exit 1
                    """
                }
            }
        }
        
        stage('Log Deployment') {
            steps {
                script {
                    echo "Logging deployment..."
                    sh """
                        echo "\$(date -u +'%Y-%m-%d %H:%M:%S UTC') | Version: ${APP_VERSION} | Build: ${env.BUILD_NUMBER} | Commit: ${GIT_COMMIT_SHORT} | Status: SUCCESS" >> ${DEPLOYMENT_LOG}
                    """
                }
            }
        }
    }
    
    post {
        success {
            echo "Pipeline completed successfully!"
            echo "Version: ${APP_VERSION}"
            echo "Image: ${REGISTRY}/${IMAGE_NAME}:${APP_VERSION}"
        }
        failure {
            echo "Pipeline failed!"
            sh """
                echo "\$(date -u +'%Y-%m-%d %H:%M:%S UTC') | Version: ${APP_VERSION} | Build: ${env.BUILD_NUMBER} | Commit: ${GIT_COMMIT_SHORT} | Status: FAILED" >> ${DEPLOYMENT_LOG}
            """
        }
        always {
            echo "Cleaning up..."
            // Optional: Clean up old images
            sh """
                podman image prune -f || true
            """
        }
    }
}

