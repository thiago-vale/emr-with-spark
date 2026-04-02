# Análise de Vulnerabilidades e Problemas no Terraform

## 🚨 CRÍTICO

### 1. **Exposição de ID da Conta AWS**
**Arquivo:** `infraestructure/iam.tf` (linha ~52)

**Problema:**
```terraform
"Resource": ["arn:aws:iam::127012818163:role/EMR_DefaultRole",
             "arn:aws:iam::127012818163:role/EMR_EC2_DefaultRole"],
```

O ID da conta (127012818163) está hardcoded na política IAM, exposto no repositório Git. Isso é uma **informação sensível** que pode ser explorada.

**Solução:**
```terraform
data "aws_caller_identity" "current" {}

"Resource": ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/EMR_DefaultRole",
             "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/EMR_EC2_DefaultRole"],
```

---

### 2. **Permissões S3 Muito Amplas**
**Arquivo:** `infraestructure/iam.tf` (linha ~40)

**Problema:**
```terraform
{
    "Effect": "Allow",
    "Action": ["s3:*"],
    "Resource": "*"
}
```

Concede acesso **completo** a **todas** as ações S3 em **todos** os buckets. Violação do princípio de menor privilégio (least privilege).

**Solução:**
```terraform
{
    "Effect": "Allow",
    "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:DeleteObject",
        "s3:ListBucket"
    ],
    "Resource": [
        "arn:aws:s3:::datalake-test-thiago",
        "arn:aws:s3:::datalake-test-thiago/*"
    ]
},
{
    "Effect": "Allow",
    "Action": ["s3:ListBucket"],
    "Resource": "arn:aws:s3:::00-terraform-state"
},
{
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:PutObject"],
    "Resource": "arn:aws:s3:::00-terraform-state/state/terraform.tfstate*"
}
```

---

### 3. **Permissões EMR Muito Amplas**
**Arquivo:** `infraestructure/iam.tf` (linha ~45)

**Problema:**
```terraform
{
    "Effect": "Allow",
    "Action": ["elasticmapreduce:*"],
    "Resource": "*"
}
```

Acesso completo a **todas** as ações EMR em **todos** os recursos.

**Solução:**
```terraform
{
    "Effect": "Allow",
    "Action": [
        "elasticmapreduce:RunJobFlow",
        "elasticmapreduce:DescribeCluster",
        "elasticmapreduce:DescribeStep",
        "elasticmapreduce:ListClusters",
        "elasticmapreduce:ListSteps"
    ],
    "Resource": "*"
}
```

---

## ⚠️ ALTO

### 4. **Runtime Python Desatualizado**
**Arquivo:** `infraestructure/lambda.tf` (linha 13)

**Problema:**
```terraform
runtime = "python3.8"
```

Python 3.8 **não é mais suportado** pela AWS Lambda (fim do suporte em dezembro/2023). Isso causará falhas no futuro.

**Solução:**
```terraform
runtime = "python3.11"
# ou
runtime = "python3.12"  # versão mais recente
```

---

### 5. **Source Code Hash Comentado**
**Arquivo:** `infraestructure/lambda.tf` (linha 9)

**Problema:**
```terraform
#   source_code_hash = filebase64sha256("lambda_function_payload.zip")
```

Sem `source_code_hash`, o Terraform **não detectará mudanças** no código da Lambda e não fará redeploy automático.

**Solução:**
```terraform
source_code_hash = filebase64sha256("lambda_function_payload.zip")
```

---

### 6. **Caminhos Relativos no Terraform**
**Arquivo:** `infraestructure/lambda.tf` (linha 2)

**Problema:**
```terraform
filename = "lambda_function_payload.zip"
```

Caminho relativo pode quebrar dependendo de onde o Terraform é executado (CI/CD, diferentes máquinas).

**Solução:**
```terraform
filename = "${path.module}/lambda_function_payload.zip"
```

---

### 7. **Falta de Configuração de Versionamento S3**
**Arquivo:** `infraestructure/provider.tf`

**Problema:** O bucket `00-terraform-state` não tem versionamento habilitado. Se alguém deletar o arquivo de estado, não há recuperação.

**Solução:** Criar um arquivo `s3.tf` com:
```terraform
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = "00-terraform-state"
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = "00-terraform-state"
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket                  = "00-terraform-state"
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

---

## ⚡ MÉDIO

### 8. **CloudWatch Logs com Acesso Total**
**Arquivo:** `infraestructure/iam.tf` (linha ~34)

**Problema:**
```terraform
{
    "Effect": "Allow",
    "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
    ],
    "Resource": "*"
}
```

Permite criar e deletar **qualquer** log group. Deveria ser restrito.

**Solução:**
```terraform
{
    "Effect": "Allow",
    "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
    ],
    "Resource": "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.lambda_function_name}:*"
}
```

---

### 9. **Memory Size Muito Baixa**
**Arquivo:** `infraestructure/lambda.tf` (linha 6)

**Problema:**
```terraform
memory_size = 128
```

128MB é muito pouco para uma Lambda que orquestra EMR. Pode causar timeouts ou erros de memória.

**Recomendação:**
```terraform
memory_size = 512  # ou 1024 para operações mais pesadas
```

---

### 10. **Timeout Muito Curto**
**Arquivo:** `infraestructure/lambda.tf` (linha 7)

**Problema:**
```terraform
timeout = 30
```

30 segundos é insuficiente para fazer a chamada `run_job_flow()` ao EMR com segurança. A requisição pode ser interrompida.

**Recomendação:**
```terraform
timeout = 60  # ou 120
```

---

### 11. **Falta de Description nas Variáveis**
**Arquivo:** `infraestructure/variables.tf`

**Problema:** Variáveis sem documentação.

**Solução:**
```terraform
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
```

---

### 12. **Falta de Outputs**
**Arquivo:** Nenhum arquivo `outputs.tf`

**Problema:** Impossível acessar valores importantes depois do deployment.

**Solução - Criar `infraestructure/outputs.tf`:**
```terraform
output "lambda_function_arn" {
  description = "ARN da função Lambda"
  value       = aws_lambda_function.executa_emr.arn
}

output "lambda_function_name" {
  description = "Nome da função Lambda"
  value       = aws_lambda_function.executa_emr.function_name
}

output "iam_role_arn" {
  description = "ARN da role IAM da Lambda"
  value       = aws_iam_role.lambda.arn
}
```

---

## ℹ️ BAIXO / BOAS PRÁTICAS

### 13. **Falta de Tags Completas**
**Arquivo:** Múltiplos

**Problema:** Recursos sem informações de projeto, ambiente, owner.

**Solução - Criar `infraestructure/locals.tf`:**
```terraform
locals {
  common_tags = {
    IES        = "IGTI"
    CURSO      = "EDC"
    Environment = "production"
    ManagedBy   = "Terraform"
    Project     = "EMR-Spark"
  }
}
```

Então usar em todos os recursos:
```terraform
tags = merge(local.common_tags, {
  Name = "Lambda EMR Orchestrator"
})
```

---

### 14. **Falta de Terraform `.gitignore`**

**Criar `infraestructure/.gitignore`:**
```
# Local .terraform directories
**/.terraform/*

# .tfstate files
*.tfstate
*.tfstate.*

# Crash log files
crash.log
crash.*.log

# Exclude all .tfvars files
*.tfvars
*.tfvars.json

# Ignore override files
override.tf
override.tf.json
*_override.tf
*_override.tf.json

# Ignore CLI configuration files
.terraformrc
terraform.rc

# Ignore plan files
*.tfplan

# Ignore package file
lambda_function_payload.zip
scripts/package/
```

---

### 15. **Falta de Validação de Versão do Terraform**
**Arquivo:** Nenhum arquivo `versions.tf`

**Solução - Criar `infraestructure/versions.tf`:**
```terraform
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

---

### 16. **Hardcoded Bucket Names**
**Arquivo:** `infraestructure/provider.tf`

**Problema:** Nome do bucket `00-terraform-state` hardcoded. Não é reutilizável em múltiplas contas AWS.

**Solução:** Usar variável com padrão:
```terraform
# em variables.tf
variable "terraform_state_bucket" {
  description = "Nome do bucket S3 para armazenar estado do Terraform"
  type        = string
  default     = "00-terraform-state"
}

# em provider.tf
backend "s3" {
  bucket = var.terraform_state_bucket  # ⚠️ NÃO FUNCIONA - backend não suporta variáveis
}
```

**Alternativa melhor:** Usar `-backend-config` na CLI:
```bash
terraform init -backend-config="bucket=my-state-bucket"
```

---

## 📋 Resumo de Ações Recomendadas

| Prioridade | Problema | Arquivo | Ação |
|-----------|----------|---------|------|
| 🚨 CRÍTICO | ID conta exposto | iam.tf | Usar `data.aws_caller_identity` |
| 🚨 CRÍTICO | S3 `s3:*` em `*` | iam.tf | Restringir a buckets específicos |
| 🚨 CRÍTICO | EMR `*` em `*` | iam.tf | Limitar ações EMR necessárias |
| ⚠️ ALTO | Python 3.8 desatualizado | lambda.tf | Atualizar para Python 3.11+ |
| ⚠️ ALTO | source_code_hash comentado | lambda.tf | Descomentar |
| ⚠️ ALTO | Caminho relativo | lambda.tf | Usar `${path.module}` |
| ⚠️ ALTO | Sem versionamento S3 | provider.tf | Criar recurso de versionamento |
| ⚡ MÉDIO | Memory/timeout baixos | lambda.tf | Aumentar para 512MB / 60s |
| ⚡ MÉDIO | CloudWatch sem restrição | iam.tf | Restringir ao log group da Lambda |
| ℹ️ BAIXO | Sem type nas variáveis | variables.tf | Adicionar `type` e `description` |
| ℹ️ BAIXO | Sem outputs | - | Criar outputs.tf |
| ℹ️ BAIXO | Sem .gitignore | infraestructure/ | Criar .gitignore |
| ℹ️ BAIXO | Sem versions.tf | infraestructure/ | Criar versions.tf |

---

## 🔍 Próximos Passos

1. Implementar correções críticas imediatamente
2. Testar com `terraform validate` e `terraform plan`
3. Usar `tflint` para validação adicional: `tflint --init && tflint`
4. Considerar usar `checkov` para análise de segurança: `checkov -d infraestructure/`
