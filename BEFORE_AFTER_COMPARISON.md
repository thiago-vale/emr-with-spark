# 📊 Comparativo Antes/Depois - Mudanças Terraform

## 🔍 Comparação Detalhada

### 1. **lambda.tf** - Correções Críticas

#### ❌ ANTES (Inseguro/Desatualizado)
```terraform
resource "aws_lambda_function" "executa_emr" {
  filename      = "lambda_function_payload.zip"      # ⚠️ Caminho relativo
  function_name = var.lambda_function_name
  role          = aws_iam_role.lambda.arn
  handler       = "lambda_function.handler"
  memory_size   = 128                                 # ⚠️ Muito baixo
  timeout       = 30                                  # ⚠️ Muito curto

#   source_code_hash = filebase64sha256("...")        # ⚠️ COMENTADO

  runtime = "python3.8"                               # ⚠️ Desatualizado (end-of-life)

  tags = {
    IES   = "IGTI"
    CURSO = "EDC"
  }
}
```

#### ✅ DEPOIS (Seguro/Moderno)
```terraform
resource "aws_lambda_function" "executa_emr" {
  filename            = "${path.module}/lambda_function_payload.zip"  # ✅ Caminho absoluto
  function_name       = var.lambda_function_name
  role                = aws_iam_role.lambda.arn
  handler             = "lambda_function.handler"
  memory_size         = 512                          # ✅ Suficiente para EMR
  timeout             = 60                           # ✅ Tempo adequado

  source_code_hash    = filebase64sha256("${path.module}/lambda_function_payload.zip")  # ✅ ATIVO

  runtime = "python3.11"                             # ✅ Suportado até 2025

  tags = {
    IES   = "IGTI"
    CURSO = "EDC"
  }
}
```

**Mudanças:**
- 🟢 Caminho relativo → Absoluto (resolve CI/CD issues)
- 🟢 Source hash descomentado (redeploy automático)
- 🟢 Memory 128MB → 512MB (não vai dar OOM)
- 🟢 Timeout 30s → 60s (suficiente para EMR)
- 🟢 Python 3.8 → 3.11 (versão suportada)

---

### 2. **iam.tf** - Permissões Restritivas (CRÍTICO)

#### ❌ ANTES (Overly Permissive)
```terraform
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"                    # ⚠️ TODOS os logs
        },
        {
            "Effect": "Allow",
            "Action": ["s3:*"],                 # ⚠️ TODAS as ações S3
            "Resource": "*"                    # ⚠️ TODOS os buckets
        },
        {
            "Effect": "Allow",
            "Action": ["elasticmapreduce:*"],   # ⚠️ TODAS as ações EMR
            "Resource": "*"                    # ⚠️ TODOS os recursos
        },
        {
          "Action": "iam:PassRole",
          "Resource": ["arn:aws:iam::127012818163:role/EMR_DefaultRole",  # ⚠️ Account ID EXPOSTO
                       "arn:aws:iam::127012818163:role/EMR_EC2_DefaultRole"],
          "Effect": "Allow"
        }
    ]
}
```

#### ✅ DEPOIS (Least Privilege)
```terraform
data "aws_caller_identity" "current" {}  # ✅ NOVO: Account ID dinâmico

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CloudWatchLogsForLambda",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.lambda_function_name}:*"  # ✅ ARN ESPECÍFICO
        },
        {
            "Sid": "S3DataLakeAccess",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",                # ✅ Ações específicas
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::datalake-test-thiago",  # ✅ Buckets específicos
                "arn:aws:s3:::datalake-test-thiago/*"
            ]
        },
        {
            "Sid": "EMRClusterManagement",
            "Effect": "Allow",
            "Action": [
                "elasticmapreduce:RunJobFlow",        # ✅ Ações específicas
                "elasticmapreduce:DescribeCluster",
                "elasticmapreduce:DescribeStep",
                "elasticmapreduce:ListClusters",
                "elasticmapreduce:ListSteps",
                "elasticmapreduce:AddJobFlowSteps",
                "elasticmapreduce:TerminateJobFlows"
            ],
            "Resource": "*"
        },
        {
            "Sid": "IAMPassRole",
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": [
                "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/EMR_DefaultRole",  # ✅ Account ID DINÂMICO
                "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/EMR_EC2_DefaultRole"
            ]
        }
    ]
}
```

**Mudanças:**
- 🟢 CloudWatch: `*` → ARN específico da Lambda
- 🟢 S3: `s3:*` → Ações específicas (get/put/delete apenas)
- 🟢 S3: `*` recursos → Buckets específicos
- 🟢 EMR: `elasticmapreduce:*` → Ações necessárias apenas
- 🟢 Account ID: Hardcoded 127012818163 → `data.aws_caller_identity` (dinâmico)
- 🟢 Remoção de: Account ID exposto no repositório

---

### 3. **variables.tf** - Documentação e Tipagem

#### ❌ ANTES (Sem documentação)
```terraform
variable "aws_region" {
  default = "us-east-1"
}

variable "lambda_function_name" {
  default = "thiagoexecutaEMRaovivo"
}
```

#### ✅ DEPOIS (Com type e description)
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
```

**Benefícios:**
- 🟢 `description`: Documentação automática
- 🟢 `type`: Validação de tipos (ex: não aceita number onde é string)
- 🟢 Melhor IDE autocomplete
- 🟢 Terraform pode validar entrada de variáveis

---

### 4. **versions.tf** - NOVO ✨

#### Criado (Não existia antes)
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

**Benefícios:**
- 🟢 Garante Terraform >= 1.0
- 🟢 Garante AWS provider ~> 5.0 (mas < 6.0)
- 🟢 Evita breaking changes de versão
- 🟢 Melhor compatibilidade em equipes

---

### 5. **outputs.tf** - NOVO ✨

#### Criado (Não existia antes)
```terraform
output "lambda_function_arn" {
  description = "ARN da função Lambda que orquestra EMR"
  value       = aws_lambda_function.executa_emr.arn
}

output "lambda_function_name" {
  description = "Nome da função Lambda"
  value       = aws_lambda_function.executa_emr.function_name
}

output "lambda_invocation_role_arn" {
  description = "ARN da role IAM usada pela Lambda"
  value       = aws_iam_role.lambda.arn
}
```

**Benefícios:**
- 🟢 Exporta valores importantes após apply
- 🟢 Fácil consulta: `terraform output lambda_function_arn`
- 🟢 Integração com outros projetos
- 🟢 Reduz necessidade de consultar AWS Console

---

### 6. **locals.tf** - NOVO ✨

#### Criado (Não existia antes)
```terraform
locals {
  common_tags = {
    IES         = "IGTI"
    CURSO       = "EDC"
    Environment = "production"
    ManagedBy   = "Terraform"
    Project     = "EMR-Spark"
  }
}
```

**Benefícios:**
- 🟢 Tags centralizadas e reutilizáveis
- 🟢 Facilita manutenção de conventions
- 🟢 Pode ser usada em todos os recursos

---

### 7. **.gitignore** - NOVO ✨

#### Criado (Não existia antes)
```
*.tfstate                              # Evita comitar arquivo de estado
*.tfstate.*                            # Evita comitar backups
lambda_function_payload.zip            # Evita comitar ZIP grande
package/                               # Evita comitar diretório de build
*.tfvars                               # Evita comitar credentials
.terraform/                            # Evita comitar cache
crash.log                              # Evita comitar crash logs
.terraformrc                           # Evita comitar config local
*.tfplan                               # Evita comitar plans
```

**Benefícios:**
- 🟢 Impede commit de `terraform.tfstate` (risco de segurança)
- 🟢 Impede commit de `lambda_function_payload.zip` (arquivo grande)
- 🟢 Impede commit de credentials em `.tfvars`
- 🟢 Impede commit de `.terraform/` (cache local)

---

## 📊 Tabela Comparativa

| Aspecto | Antes | Depois | Status |
|--------|-------|--------|--------|
| **Segurança** | ⛔ Crítica (s3:*, EMR:*, exposto ID) | ✅ Mínimo privilégio | Corrigido |
| **Confiabilidade** | ⚠️ Python 3.8 EOL | ✅ Python 3.11 | Atualizado |
| **Automação** | ❌ Sem source_code_hash | ✅ Com tracking de mudanças | Ativado |
| **Docs/Type** | ❌ Sem descriptions | ✅ Todas descritas | Adicionado |
| **Outputs** | ❌ Sem outputs.tf | ✅ Com outputs | Criado |
| **Git** | ⚠️ Sem .gitignore | ✅ Com proteção | Criado |
| **Versions** | ❌ Sem validação | ✅ Com versions.tf | Criado |
| **Performance** | ⚠️ 128MB/30s | ✅ 512MB/60s | Aumentado |
| **Paths** | ⚠️ Caminho relativo | ✅ ${path.module} | Corrigido |

---

## 🎯 Impacto das Mudanças

### Segurança: ⬆️⬆️⬆️ Muito Alto
- ✅ Permissões IAM reduzidas de "tudo" para "necessário apenas"
- ✅ Account ID não exposto em repositório Git
- ✅ CloudWatch logs restrito ao log group da Lambda

### Confiabilidade: ⬆️⬆️ Alto
- ✅ Python 3.11 com suporte estendido
- ✅ Memory e timeout adequados para operações
- ✅ Source code hash garante redeploy automático

### Manutenibilidade: ⬆️⬆️ Alto
- ✅ Descrições em variáveis
- ✅ Outputs para referência
- ✅ Locals para conventions centralizadas
- ✅ .gitignore para evitar commits indevidos

### DevOps: ⬆️ Médio
- ✅ Versions.tf para reproducibilidade
- ✅ Caminhos absolutos para CI/CD
- ✅ Melhor estrutura para equipes

---

## ✅ Validações Executadas

```
✓ terraform validate      → Success! The configuration is valid.
✓ terraform fmt -check    → All files formatted correctly
```

**Pronto para deploy!**
