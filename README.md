# EMR-with-Spark

[![Terraform Validate](https://img.shields.io/badge/terraform-validate-success?style=flat-square)](infraestructure/)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![AWS](https://img.shields.io/badge/AWS-Certified-FF9900?style=flat-square&logo=amazonaws)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python)](https://www.python.org/)

Framework de automação serverless para orquestração de pipelines **Spark** no AWS EMR (Elastic MapReduce), disparados por funções **Lambda** e gerenciados por **Terraform**.

## 🎯 Propósito

Simplificar a execução de fluxos de trabalho de processamento de **big data** usando:
- **AWS Lambda** como orquestrador sem servidor
- **AWS EMR** para processamento distribuído com Spark
- **Terraform** para infraestrutura como código
- **GitHub Actions** para CI/CD automático

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│  GitHub / AWS Console / Scheduler                              │
│           │                                                    │
│           ▼                                                    │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  AWS Lambda (Python 3.11)                             │   │
│  │  - Orquestra job flows EMR                            │   │
│  │  - Configura clusters com Spark                       │   │
│  │  - Dispara steps de processamento                     │   │
│  └────────────────────────────────────────────────────────┘   │
│           │                                                    │
│           ▼                                                    │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  AWS EMR (emr-7.2.0)                                  │   │
│  │  - Master + Core nodes (m5.xlarge SPOT)              │   │
│  │  - Spark, Hive, Pig, Hue, Livy                       │   │
│  │  - AWS Glue Data Catalog                             │   │
│  └────────────────────────────────────────────────────────┘   │
│           │                                                    │
│           ├─────────────────────────────────┬──────┐           │
│           ▼                                 ▼      ▼           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────┐     │
│  │ PySpark Job 1    │  │ PySpark Job 2    │  │ Delta    │     │
│  │ Delta Insert     │  │ UPSERT           │  │ Lake     │     │
│  └──────────────────┘  └──────────────────┘  └──────────┘     │
│           │                                                    │
│           ▼                                                    │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  AWS S3 (Data Lake)                                   │   │
│  │  - Código: s3://datalake-test-thiago/98-codes/       │   │
│  │  - Logs: s3://datalake-test-thiago/99-logs/          │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✨ Características

- ✅ **Serverless** - Lambda executa sob demanda
- ✅ **Infrastructure as Code** - Terraform gerencia tudo
- ✅ **CI/CD Automático** - GitHub Actions valida e deploya
- ✅ **Delta Lake** - Suporte ACID no Spark
- ✅ **Segurança** - Permissões IAM restritivas
- ✅ **Monitoramento** - Logs centralizados
- ✅ **Cost Optimized** - Instâncias SPOT

---

## 📋 Pré-requisitos

### Local
- Terraform >= 1.0
- AWS CLI v2 configurado
- Python 3.11+
- Git, Bash

### AWS
- Conta ativa com permissões IAM
- VPC e subnet já criadas
- Roles EMR: `EMR_DefaultRole` e `EMR_EC2_DefaultRole`
- EC2 key pair: `thiago-teste`

### GitHub
- Secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

---

## 🚀 Instalação Rápida

```bash
# Clonar
git clone https://github.com/seu-usuario/emr-with-spark.git
cd emr-with-spark

# AWS Config
aws configure

# Deploy
cd infraestructure
terraform init
terraform validate
terraform apply
```

---

## ⚙️ Configuração

### Variáveis Terraform

Edite `infraestructure/variables.tf`:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `aws_region` | `us-east-1` | Região AWS |
| `lambda_function_name` | `thiagoexecutaEMRaovivo` | Nome Lambda |
| `key_pair_name` | `thiago-teste` | EC2 Key Pair |
| `airflow_subnet_id` | `subnet-4cef5427` | Subnet EMR |
| `vpc_id` | `vpc-d724b4bc` | VPC ID |

### Modificar Lambda

```bash
# 1. Editar código
vim src/lambda_function.py

# 2. Reconstruir
sh scripts/build_lambda_package.sh

# 3. Redeploy
cd infraestructure && terraform apply
```

### Adicionar Dependências

```bash
# 1. Editar
vim src/lambda_requirements.txt

# 2. Reconstruir
sh scripts/build_lambda_package.sh

# 3. Redeploy
cd infraestructure && terraform apply
```

---

## 📖 Uso

### Disparar Lambda

```bash
aws lambda invoke \
  --function-name thiagoexecutaEMRaovivo \
  --region us-east-1 \
  response.json

cat response.json
```

### Monitorar

```bash
# Logs Lambda
aws logs tail /aws/lambda/thiagoexecutaEMRaovivo --follow

# EMR Clusters
aws emr list-clusters --region us-east-1

# S3 Logs
aws s3 ls s3://datalake-test-thiago/99-logs/
```

---

## 📁 Estrutura

```
emr-with-spark/
├── README.md                      # Este arquivo
├── .github/
│   ├── workflows/
│   │   ├── deploy.yaml            # Deploy automático
│   │   └── test.yaml              # Validação PR
│   └── copilot-instructions.md    # Instruções IA
│
├── src/
│   ├── lambda_function.py         # Lambda handler
│   └── lambda_requirements.txt     # Dependências
│
├── scripts/
│   ├── build_lambda_package.sh    # Build script
│   └── package/                   # Build dir (gerado)
│
└── infraestructure/
    ├── .gitignore
    ├── provider.tf
    ├── variables.tf
    ├── outputs.tf
    ├── versions.tf
    ├── locals.tf
    ├── lambda.tf
    └── iam.tf
```

---

## 🔧 Fluxo de Desenvolvimento

### 1. Editar código

```bash
vim src/lambda_function.py
sh scripts/build_lambda_package.sh
cd infraestructure && terraform plan
```

### 2. Commit e push

```bash
git add .
git commit -m "feat: nova funcionalidade"
git push origin main
```

### 3. GitHub Actions valida

- **PR**: `test.yaml` - valida sem aplicar
- **Master merge**: `deploy.yaml` - valida, reconstrói, aplica

### 4. Lambda atualizada automaticamente

✅ Pronto para usar!

---

## 🐛 Troubleshooting

### Lambda ZIP não encontrado

```bash
sh scripts/build_lambda_package.sh
cd infraestructure && terraform apply
```

### Erro de permissão S3

```bash
# Ver política
aws iam get-role-policy \
  --role-name thiago-lambda-role \
  --policy-name thiago-lambda-policy

# Editar infraestructure/iam.tf e adicionar permissão
```

### EMR Roles não existem

```bash
aws iam get-role --role-name EMR_DefaultRole
aws iam get-role --role-name EMR_EC2_DefaultRole
```

Criar via AWS Console se não existirem.

### Terraform state corrompido

```bash
# Backup
aws s3 cp s3://00-terraform-state/state/terraform.tfstate terraform.tfstate.backup

# Remover lock
terraform force-unlock <LOCK_ID>

# Retry
terraform apply
```

---

## 📊 Custos (US-EAST-1)

| Recurso | Custo | Notas |
|---------|-------|-------|
| Lambda | $0.20/1M | 512MB, 60s |
| EMR | $10-50/h | Depende tamanho |
| S3 | $0.023/GB/mês | Storage |
| CloudWatch | $0.50/GB | Logs |
| **Total** | $100-500/mês | Varia uso |

**Otimizações:**
- ✅ SPOT instances (80% desconto)
- ✅ Cluster termina auto
- ✅ Lambda paga por tempo
- ✅ S3 versioning para recovery

---

## 🔐 Segurança

✅ **Least Privilege** - Permissões mínimas
✅ **No Hardcoding** - Account ID dinâmico
✅ **Secret Protection** - .gitignore credentials
✅ **Encryption** - Terraform state criptografado
✅ **State Locking** - Protege corrupção

---

## 📚 Documentação

- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Instruções para agents IA
- [TERRAFORM_ANALYSIS.md](TERRAFORM_ANALYSIS.md) - Análise de vulnerabilidades
- [TERRAFORM_MIGRATION.md](TERRAFORM_MIGRATION.md) - Guia de migração
- [BEFORE_AFTER_COMPARISON.md](BEFORE_AFTER_COMPARISON.md) - Antes/depois

---

## 💡 Exemplos

### Job Spark Customizado

Edite `src/lambda_function.py`:

```python
Steps=[{
    'Name': 'Meu Job',
    'ActionOnFailure': 'CONTINUE',
    'HadoopJarStep': {
        'Jar': 'command-runner.jar',
        'Args': ['spark-submit',
                 '--packages', 'io.delta:delta-core_2.12:1.0.0',
                 's3://datalake-test-thiago/98-codes/.../meu_script.py'
                 ]
    }
}]
```

Reconstrua e redeploy:

```bash
sh scripts/build_lambda_package.sh
cd infraestructure && terraform apply
```

### Agendar com EventBridge

```bash
aws events put-rule \
  --name daily-emr-job \
  --schedule-expression "cron(0 8 * * ? *)"

aws events put-targets \
  --rule daily-emr-job \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:ACCOUNT:function:thiagoexecutaEMRaovivo"
```

---

## 🤝 Contribuindo

1. Fork o projeto
2. Branch: `git checkout -b feature/sua-feature`
3. Commit: `git commit -m 'feat: descrição'`
4. Push: `git push origin feature/sua-feature`
5. Pull Request

**Checklist:**
- ✅ `terraform validate`
- ✅ `terraform fmt`
- ✅ Docs atualizados
- ✅ Sem arquivos sensíveis

---

## 📞 Suporte

- 🐛 [Issues](../../issues)
- 💬 [Discussions](../../discussions)

---

## 📄 Licença

MIT License - veja [LICENSE](LICENSE)

---

## 🙏 Agradecimentos

- AWS - Infraestrutura
- Terraform - IaC
- Apache Spark - Processamento
- GitHub Actions - Automação

---

**Status:** ✅ Produção
**Última atualização:** 1 de abril de 2026
**Mantido por:** Thiago Vale
