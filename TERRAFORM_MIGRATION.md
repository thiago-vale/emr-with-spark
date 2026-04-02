# Guia de Migração - Correções de Segurança no Terraform

## 📋 Resumo das Mudanças Aplicadas

### Arquivos Modificados

#### 1. **infraestructure/variables.tf**
✅ Adicionadas `type` e `description` em todas as variáveis
- Melhora legibilidade e documentação
- Habilita validação de tipos

#### 2. **infraestructure/lambda.tf**
✅ **Caminho do arquivo:** `"lambda_function_payload.zip"` → `"${path.module}/lambda_function_payload.zip"`
  - Resolve problemas com caminhos relativos em CI/CD

✅ **Source Code Hash:** Descomentado `source_code_hash`
  - Lambda agora refaz deploy automaticamente quando código muda

✅ **Memory:** 128MB → 512MB
  - Previne erros de memória em operações pesadas

✅ **Timeout:** 30s → 60s
  - Suficiente para chamadas ao EMR sem interrupções

✅ **Runtime:** `python3.8` → `python3.11`
  - Python 3.8 não é mais suportado pela AWS

#### 3. **infraestructure/iam.tf** 🔐 CRÍTICO
✅ **Adicionado Data Source:** `data "aws_caller_identity" "current" {}`
  - Obtém Account ID dinamicamente (remove exposição de ID hardcoded)

✅ **CloudWatch Logs:** `Resource: "*"` → ARN específico
  - Antes: acesso a TODOS os logs
  - Depois: acesso apenas ao log group da Lambda

✅ **S3 Permissions:** `"s3:*"` em `*` → Ações específicas em buckets específicos
  - Antes: acesso total a todos os buckets AWS
  - Depois: apenas `GetObject`, `PutObject`, `DeleteObject` nos buckets necessários

✅ **EMR Permissions:** `"elasticmapreduce:*"` em `*` → Ações específicas
  - Antes: acesso total a EMR
  - Depois: apenas `RunJobFlow`, `DescribeCluster`, etc.

✅ **IAM PassRole:** Account ID dinâmico
  - Antes: `"arn:aws:iam::127012818163:role/..."`
  - Depois: `"arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/..."`

### Arquivos Criados

#### 4. **infraestructure/versions.tf** ✨ NOVO
- Define versão mínima do Terraform (>= 1.0)
- Define provider AWS com versão locked (~> 5.0)
- Garante compatibilidade e evita surpresas

#### 5. **infraestructure/outputs.tf** ✨ NOVO
- Exporta ARN da Lambda
- Exporta nome da Lambda
- Exporta ARN da role IAM
- Facilita referência cruzada com outros projetos

#### 6. **infraestructure/locals.tf** ✨ NOVO
- Define `common_tags` reutilizável
- Centraliza conventions de tagging
- Facilita manutenção

#### 7. **infraestructure/.gitignore** ✨ NOVO
- Previne commit de `terraform.tfstate`
- Previne commit de `lambda_function_payload.zip`
- Previne commit de credentials em `.tfvars`

---

## 🔍 Como Validar as Mudanças

### 1. Validar Sintaxe do Terraform
```bash
cd infraestructure
terraform validate
```

**Resultado esperado:**
```
Success! The configuration is valid.
```

---

### 2. Validar Formatação
```bash
terraform fmt -check -recursive
```

Se houver diferenças:
```bash
terraform fmt -recursive  # Formata automaticamente
```

---

### 3. Planejar Mudanças (Dry-run)
```bash
terraform init
terraform plan -out=tfplan
```

**O que observar:**
- Lambda deve mostrar mudança de runtime python3.8 → python3.11
- Permissões IAM devem mudar (mais restritivas)
- Nenhum recurso deve ser destruído

---

### 4. Usar TFLint (Recomendado)
```bash
# Instalar tflint
curl https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash

# Executar validação
cd infraestructure
tflint
```

---

### 5. Usar Checkov para Análise de Segurança
```bash
# Instalar checkov
pip install checkov

# Executar análise
checkov -d infraestructure/
```

---

## ⚠️ Passos de Deployment

### **ANTES de fazer deploy:**

1. **Backup do estado do Terraform:**
   ```bash
   aws s3 cp s3://00-terraform-state/state/terraform.tfstate terraform.tfstate.backup
   ```

2. **Revisar plan:**
   ```bash
   terraform plan
   ```
   ✅ Verificar se não há surpresas

3. **Testar localmente:**
   ```bash
   terraform validate
   terraform fmt -check
   ```

### **Deployment:**

```bash
cd infraestructure
terraform apply tfplan
```

### **DEPOIS de fazer deploy:**

1. **Verificar output:**
   ```bash
   terraform output
   ```

2. **Testar invocação da Lambda:**
   ```bash
   aws lambda invoke \
     --function-name thiagoexecutaEMRaovivo \
     --region us-east-1 \
     response.json
   
   cat response.json
   ```

3. **Monitorar logs:**
   ```bash
   aws logs tail /aws/lambda/thiagoexecutaEMRaovivo --follow
   ```

---

## 🚨 Mudanças Importantes

### Python 3.8 → 3.11
Certifique-se de que `src/lambda_requirements.txt` é compatível com Python 3.11:
```bash
# Testar localmente
python3.11 -m pip install -r src/lambda_requirements.txt
```

### Permissões IAM Mais Restritivas
Se a Lambda falhar com erro de permissão:
1. Verifique CloudWatch Logs
2. Adicione permissão necessária em `iam.tf`
3. Reconstrua e redeploy

### Source Code Hash
Toda mudança em `src/lambda_function.py` vai:
1. Gerar novo hash
2. Forçar rebuild do Terraform
3. Fazer redeploy automático ✅

---

## 📚 Arquivos de Referência

| Arquivo | Propósito |
|---------|-----------|
| `versions.tf` | Versões do Terraform e providers |
| `variables.tf` | Variáveis de entrada com validação |
| `locals.tf` | Valores locais reutilizáveis |
| `provider.tf` | Configuração de provider AWS |
| `lambda.tf` | Recurso da função Lambda |
| `iam.tf` | Roles e policies IAM |
| `outputs.tf` | Valores exportados |
| `.gitignore` | Arquivos a não commitar |

---

## ✅ Checklist de Migração

- [ ] Validou com `terraform validate`
- [ ] Rodou `terraform plan` e revisou mudanças
- [ ] Fez backup do estado (tfstate)
- [ ] Buildou novo package Lambda: `sh scripts/build_lambda_package.sh`
- [ ] Rodou `terraform apply`
- [ ] Verificou output com `terraform output`
- [ ] Testou invocação da Lambda
- [ ] Verificou logs em CloudWatch
- [ ] Commitou mudanças (agora com `.gitignore`)

---

## 🆘 Troubleshooting

### Erro: "source_code_hash mismatch"
```bash
# Reconstrua o pacote
sh scripts/build_lambda_package.sh

# Então applique novamente
terraform apply
```

### Erro: "Permission denied" em S3
Verificar se Lambda consegue acessar os buckets:
```bash
aws s3 ls s3://datalake-test-thiago/99-logs/
aws s3 ls s3://datalake-test-thiago/98-codes/
```

### Erro: "EMR role not found"
Verificar se as roles EMR existem:
```bash
aws iam get-role --role-name EMR_DefaultRole
aws iam get-role --role-name EMR_EC2_DefaultRole
```

---

## 📖 Referências

- [Terraform Best Practices](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Lambda Runtime Support](https://docs.aws.amazon.com/lambda/latest/dg/runtime-support-policy.html)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Checkov](https://www.checkov.io/)
- [TFLint](https://github.com/terraform-linters/tflint)
