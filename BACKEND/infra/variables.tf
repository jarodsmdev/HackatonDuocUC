variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type    = string
  default = "hackatonduocuc"
}

variable "instance_type" {
  type    = string
  default = "t3.large"
}

# Usa una AMI Ubuntu actual (puedes ajustar según región)
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical (Ubuntu)
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

# Clave SSH para acceder
variable "ssh_key_name" {
  description = "Nombre del par de claves SSH existente en AWS"
  type        = string
  default     = "HACKATON_KEY"
}

# Tu IP pública local (para restringir SSH)
variable "my_ip" {
  type    = string
  default = "0.0.0.0/0" # ⚠️ cambia a tu IP real para seguridad
}
