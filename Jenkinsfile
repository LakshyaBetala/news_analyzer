// CloudForge CD pipeline:
//   test -> terraform -> quality gate -> docker build -> deploy to Kubernetes (k3s) -> canary -> record release
// TARGET=local : AWS is emulated by LocalStack, Kubernetes is the k3s container from docker-compose.yml (free, no account)
// TARGET=aws   : real AWS. Needs Jenkins credentials 'aws-credentials' (username/password = access key id/secret)
//                and 'ec2-ssh-key' (SSH username with private key, user "ubuntu").
pipeline {
    agent any

    triggers { pollSCM('* * * * *') }   // push to GitHub -> build starts within a minute, no webhook needed

    parameters {
        choice(name: 'TARGET', choices: ['local', 'aws'], description: 'local = LocalStack + k3s container, aws = real AWS')
        string(name: 'AWS_REGION', defaultValue: 'ap-south-1', description: 'AWS region')
        string(name: 'SSH_CIDR', defaultValue: '0.0.0.0/0', description: '(aws) CIDR allowed to SSH to EC2')
        string(name: 'PUBLIC_KEY_PATH', defaultValue: '/var/jenkins_home/cloudforge.pub', description: '(aws) public key installed on EC2')
    }

    environment {
        IMAGE_NAME  = 'news-analyzer'
        GIT_SHORT   = "${env.GIT_COMMIT ? env.GIT_COMMIT.take(7) : 'local'}"
        APP_VERSION = "${env.BUILD_NUMBER}.${GIT_SHORT}"
        TF_IN_AUTOMATION = '1'
        RELEASE_STATUS   = 'BLOCKED'   // flipped to PROMOTED / ROLLED_BACK as the run progresses
    }

    stages {
        stage('Test') {
            steps {
                sh '''
                    rm -f eval_result.json smoke.json releases.json
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -q -r requirements.txt
                    pytest tests/ -q
                '''
            }
        }

        stage('Provision (Terraform)') {
            steps {
                script {
                    withTarget {
                        dir('infra') {
                            sh 'terraform init -input=false'
                            sh 'terraform apply -auto-approve -input=false'
                            env.BUCKET = sh(script: 'terraform output -raw reports_bucket', returnStdout: true).trim()
                            env.EC2_IP = sh(script: 'terraform output -raw public_ip', returnStdout: true).trim()
                            env.INSTANCE_ID = sh(script: 'terraform output -raw instance_id', returnStdout: true).trim()
                        }
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                script {
                    withTarget {
                        sh '''
                            aws s3 cp s3://$BUCKET/releases.json releases.json || echo "no release history yet"
                            . .venv/bin/activate
                            python eval/run_eval.py --baseline releases.json --out eval_result.json
                        '''
                    }
                }
            }
        }

        stage('Build Image') {
            steps {
                sh 'docker build -t $IMAGE_NAME:$APP_VERSION .'
            }
        }

        stage('Deploy (Kubernetes)') {
            steps {
                script {
                    withTarget {
                        sh '''
                            for i in $(seq 1 60); do
                                $RUN k3s kubectl get nodes 2>/dev/null | grep -q " Ready" && exit 0
                                echo "waiting for Kubernetes... ($i)"; sleep 10
                            done
                            exit 1
                        '''
                        // ship the image straight into the cluster's containerd: no registry needed
                        sh 'docker save $IMAGE_NAME:$APP_VERSION | $RUN k3s ctr images import -'
                        sh '''
                            sed -e "s#__IMAGE__#docker.io/library/$IMAGE_NAME:$APP_VERSION#" \
                                -e "s#__VERSION__#$APP_VERSION#" \
                                -e "s#__BUCKET__#$BUCKET#" \
                                -e "s#__REGION__#$AWS_DEFAULT_REGION#" \
                                -e "s#__S3_ENDPOINT__#$S3_ENDPOINT#" k8s/app.yaml \
                              | $RUN k3s kubectl apply -f -
                        '''
                        int rc = sh(returnStatus: true, script: '$RUN k3s kubectl rollout status deployment/news-analyzer --timeout=180s')
                        if (rc != 0) {
                            sh '$RUN k3s kubectl rollout undo deployment/news-analyzer || true'
                            env.RELEASE_STATUS = 'ROLLED_BACK'
                            error('Rollout failed, rolled back')
                        }
                    }
                }
            }
        }

        stage('Canary Check') {
            steps {
                script {
                    withTarget {
                        int rc = sh(returnStatus: true, script: '''
                            . .venv/bin/activate
                            python scripts/smoke_test.py $APP_URL --out smoke.json
                        ''')
                        if (rc != 0) {
                            sh '$RUN k3s kubectl rollout undo deployment/news-analyzer || true'
                            env.RELEASE_STATUS = 'ROLLED_BACK'
                            error('Canary failed, rolled back')
                        }
                        env.RELEASE_STATUS = 'PROMOTED'
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                if (env.BUCKET) {
                    withTarget {
                        sh '''
                            . .venv/bin/activate 2>/dev/null || true
                            CPU_ARG=""
                            if [ "$TARGET" = "aws" ] && [ -n "$INSTANCE_ID" ]; then
                                CPU=$(aws cloudwatch get-metric-statistics --namespace AWS/EC2 --metric-name CPUUtilization \
                                      --dimensions Name=InstanceId,Value=$INSTANCE_ID \
                                      --start-time $(date -u -d '-15 minutes' +%FT%TZ) --end-time $(date -u +%FT%TZ) \
                                      --period 900 --statistics Average --query 'Datapoints[0].Average' --output text || echo None)
                                case "$CPU" in None|"") ;; *) CPU_ARG="--cpu $(printf '%.1f' $CPU)";; esac
                            fi
                            python scripts/record_release.py --version "$APP_VERSION" --commit "$GIT_SHORT" \
                                --message "$(git log -1 --pretty=%s)" --status "$RELEASE_STATUS" \
                                --eval eval_result.json --smoke smoke.json $CPU_ARG
                            aws s3 cp releases.json s3://$BUCKET/releases.json
                            if [ -f eval_result.json ]; then
                                ACC=$(python -c "import json;print(round(json.load(open('eval_result.json'))['accuracy']*100,1))")
                                aws cloudwatch put-metric-data --namespace CloudForge --metric-name AccuracyPercent --value $ACC
                            fi
                        '''
                    }
                }
            }
        }
        success { echo "Released ${APP_VERSION}: PROMOTED" }
        failure { echo "Release ${APP_VERSION} did not ship (${env.RELEASE_STATUS}). The previous version is still live." }
    }
}

// Sets up the environment for the chosen target, then runs the body.
def withTarget(Closure body) {
    if (params.TARGET == 'aws') {
        withCredentials([
            usernamePassword(credentialsId: 'aws-credentials', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY'),
            sshUserPrivateKey(credentialsId: 'ec2-ssh-key', keyFileVariable: 'SSH_KEY')
        ]) {
            withEnv([
                "TARGET=aws",
                "AWS_DEFAULT_REGION=${params.AWS_REGION}",
                "TF_VAR_region=${params.AWS_REGION}",
                "TF_VAR_ssh_cidr=${params.SSH_CIDR}",
                "TF_VAR_public_key_path=${params.PUBLIC_KEY_PATH}",
                "RUN=ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no -o ConnectTimeout=10 ubuntu@${env.EC2_IP} sudo",
                "APP_URL=http://${env.EC2_IP}",
                "S3_ENDPOINT="
            ]) { body() }
        }
    } else {
        withEnv([
            "TARGET=local",
            "AWS_ACCESS_KEY_ID=test",
            "AWS_SECRET_ACCESS_KEY=test",
            "AWS_DEFAULT_REGION=${params.AWS_REGION}",
            "AWS_ENDPOINT_URL=http://localstack:4566",
            "TF_VAR_local_mode=true",
            "TF_VAR_localstack_endpoint=http://localstack:4566",
            "TF_VAR_region=${params.AWS_REGION}",
            "RUN=docker exec -i cloudforge-k3s",
            "APP_URL=http://cloudforge-k3s",
            // pods can't resolve compose service names, so hand them LocalStack's IP
            "S3_ENDPOINT=http://${sh(script: "getent hosts localstack | awk '{print \$1}'", returnStdout: true).trim()}:4566"
        ]) { body() }
    }
}
