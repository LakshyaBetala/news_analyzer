output "public_ip" {
  value = try(aws_eip.app[0].public_ip, "")
}

output "reports_bucket" {
  value = aws_s3_bucket.reports.bucket
}

output "instance_id" {
  value = try(aws_instance.app[0].id, "")
}
