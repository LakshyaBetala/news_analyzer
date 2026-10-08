# Jenkins with every tool the Jenkinsfile needs: docker CLI, terraform, aws cli, python, ssh,
# plus plugins and a pre-created pipeline job (see casc.yaml).
FROM jenkins/jenkins:lts-jdk17
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
        docker-cli python3 python3-venv python3-pip openssh-client unzip curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://releases.hashicorp.com/terraform/1.9.8/terraform_1.9.8_linux_amd64.zip -o /tmp/tf.zip \
    && unzip /tmp/tf.zip -d /usr/local/bin && rm /tmp/tf.zip
RUN curl -sSL https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o /tmp/aws.zip \
    && unzip -q /tmp/aws.zip -d /tmp && /tmp/aws/install && rm -rf /tmp/aws /tmp/aws.zip
# runs as root so it can use the mounted /var/run/docker.sock
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"
RUN jenkins-plugin-cli --plugins workflow-aggregator git credentials-binding configuration-as-code job-dsl pipeline-stage-view
