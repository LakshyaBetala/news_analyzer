terraform {
  required_version = ">= 1.5"
  required_providers {
    aws    = { source = "hashicorp/aws", version = "~> 5.0" }
    random = { source = "hashicorp/random", version = "~> 3.0" }
  }
}

# Two targets, one codebase:
#   local_mode = true   -> S3 / IAM / CloudWatch are created inside LocalStack (free AWS emulator); no EC2
#   local_mode = false  -> real AWS, including the EC2 instance that runs Kubernetes
provider "aws" {
  region                      = var.region
  access_key                  = var.local_mode ? "test" : null
  secret_key                  = var.local_mode ? "test" : null
  skip_credentials_validation = var.local_mode
  skip_metadata_api_check     = var.local_mode
  skip_requesting_account_id  = var.local_mode
  s3_use_path_style           = var.local_mode

  dynamic "endpoints" {
    for_each = var.local_mode ? [1] : []
    content {
      s3             = var.localstack_endpoint
      iam            = var.localstack_endpoint
      cloudwatch     = var.localstack_endpoint
      cloudwatchlogs = var.localstack_endpoint
      sts            = var.localstack_endpoint
    }
  }
}

locals {
  name   = "cloudforge"
  on_aws = !var.local_mode
}

# ---------- S3: release history ----------
resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "reports" {
  bucket        = "${local.name}-reports-${random_id.suffix.hex}"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "reports" {
  bucket                  = aws_s3_bucket.reports.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ---------- IAM: the pods read releases.json through the instance role ----------
resource "aws_iam_role" "ec2" {
  name = "${local.name}-ec2-role"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Action = "sts:AssumeRole", Principal = { Service = "ec2.amazonaws.com" } }]
  })
}

resource "aws_iam_role_policy" "reports_read" {
  name = "reports-read"
  role = aws_iam_role.ec2.id
  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Action = ["s3:GetObject"], Resource = "${aws_s3_bucket.reports.arn}/*" }]
  })
}

resource "aws_iam_instance_profile" "ec2" {
  name = "${local.name}-profile"
  role = aws_iam_role.ec2.name
}

# ---------- CloudWatch: model quality, pushed by the pipeline on every release ----------
resource "aws_cloudwatch_log_group" "pipeline" {
  name              = "/cloudforge/pipeline"
  retention_in_days = 14
}

resource "aws_cloudwatch_metric_alarm" "accuracy_low" {
  alarm_name          = "${local.name}-accuracy-low"
  alarm_description   = "Model accuracy of the latest release is below 85%"
  namespace           = "CloudForge"
  metric_name         = "AccuracyPercent"
  statistic           = "Minimum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 85
  comparison_operator = "LessThanThreshold"
  treat_missing_data  = "notBreaching"
}

# ---------- Real AWS only: network, EC2 running single-node Kubernetes (k3s), CPU monitoring ----------
resource "aws_security_group" "app" {
  count       = local.on_aws ? 1 : 0
  name        = "${local.name}-sg"
  description = "SSH from the operator, HTTP from everywhere"

  ingress {
    description = "SSH (Jenkins + operator)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_cidr]
  }
  ingress {
    description = "HTTP to the app"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_key_pair" "deploy" {
  count      = local.on_aws ? 1 : 0
  key_name   = "${local.name}-key"
  public_key = file(pathexpand(var.public_key_path))
}

data "aws_ami" "ubuntu" {
  count       = local.on_aws ? 1 : 0
  most_recent = true
  owners      = ["099720109477"] # Canonical
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_instance" "app" {
  count                  = local.on_aws ? 1 : 0
  ami                    = data.aws_ami.ubuntu[0].id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.deploy[0].key_name
  vpc_security_group_ids = [aws_security_group.app[0].id]
  iam_instance_profile   = aws_iam_instance_profile.ec2.name
  monitoring             = true # 1-minute CloudWatch metrics

  # hop limit 2 lets pods (one network hop behind the node) reach the instance role
  metadata_options {
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
  }

  root_block_device {
    volume_size = 20
  }

  user_data = <<-EOF
    #!/bin/bash
    set -eux
    curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--disable traefik --write-kubeconfig-mode 644" sh -
    touch /var/lib/cloudforge-ready
  EOF

  tags = { Name = "${local.name}-app" }
}

resource "aws_eip" "app" {
  count    = local.on_aws ? 1 : 0
  instance = aws_instance.app[0].id
}

resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  count               = local.on_aws ? 1 : 0
  alarm_name          = "${local.name}-cpu-high"
  alarm_description   = "EC2 CPU above 80% for 10 minutes"
  namespace           = "AWS/EC2"
  metric_name         = "CPUUtilization"
  dimensions          = { InstanceId = aws_instance.app[0].id }
  statistic           = "Average"
  period              = 300
  evaluation_periods  = 2
  threshold           = 80
  comparison_operator = "GreaterThanThreshold"
}

resource "aws_cloudwatch_dashboard" "main" {
  count          = local.on_aws ? 1 : 0
  dashboard_name = local.name
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title   = "EC2 CPU"
          region  = var.region
          stat    = "Average"
          period  = 60
          metrics = [["AWS/EC2", "CPUUtilization", "InstanceId", aws_instance.app[0].id]]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title   = "Model accuracy per release (%)"
          region  = var.region
          stat    = "Maximum"
          period  = 300
          metrics = [["CloudForge", "AccuracyPercent"]]
        }
      }
    ]
  })
}
