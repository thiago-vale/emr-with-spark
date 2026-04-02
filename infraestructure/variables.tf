variable "aws_region" {
  description = "Região AWS para deployment"
  type        = string
  default     = "us-east-1"
}

variable "lambda_function_name" {
  description = "Nome da função Lambda que orquestra EMR"
  type        = string
  default     = "thiagoexecutaEMRaovivo"
}

variable "key_pair_name" {
  description = "Nome do key pair EC2 para acesso ao cluster EMR"
  type        = string
  default     = "thiago-teste"
}

variable "airflow_subnet_id" {
  description = "ID da subnet para instâncias EMR"
  type        = string
  default     = "subnet-4cef5427"
}

variable "vpc_id" {
  description = "ID da VPC para o cluster EMR"
  type        = string
  default     = "vpc-d724b4bc"
}