provider "aws" {
  region = var.aws_region
}


# Centralizar o arquivo de controle de estado do terraform
terraform {
  backend "s3" {
    bucket       = "00-terraform-state"
    key          = "state/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
}