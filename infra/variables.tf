variable "local_mode" {
  description = "true = emulate AWS with LocalStack (free, no account); false = real AWS"
  type        = bool
  default     = false
}

variable "localstack_endpoint" {
  description = "LocalStack URL as seen from where Terraform runs"
  type        = string
  default     = "http://localhost:4566"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "instance_type" {
  description = "k3s needs about 1 GB RAM; t3.small is the smallest comfortable size"
  type        = string
  default     = "t3.small"
}

variable "public_key_path" {
  description = "SSH public key installed on the instance (the private key goes into Jenkins). Real AWS only."
  type        = string
  default     = "~/.ssh/cloudforge.pub"
}

variable "ssh_cidr" {
  description = "CIDR allowed to SSH in, e.g. 203.0.113.7/32. Must include your Jenkins machine. Real AWS only."
  type        = string
  default     = "0.0.0.0/0"
}
