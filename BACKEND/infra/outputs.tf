output "instance_public_ip" {
  value = data.aws_eip.existing_ip.public_ip
}

output "ssh_connection" {
  value = "ssh -i ~/.ssh/your-key.pem ubuntu@${data.aws_eip.existing_ip.public_ip}"
}
