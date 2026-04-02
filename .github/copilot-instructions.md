# Instruções Copilot para EMR-with-Spark

## Visão Geral do Projeto

**Propósito:** Framework de automação AWS Lambda + EMR (Elastic MapReduce) que dispara fluxos de trabalho Spark para pipelines de processamento de dados.

**Arquitetura:** Processamento de big data acionado por serverless:
- Função Lambda (Python 3.8) atua como orquestrador
- Dispara clusters EMR configurados com Spark, Hive, Pig e Delta Lake
- Infraestrutura gerenciada via Terraform com estado remoto em S3
- Deploy contínuo via GitHub Actions em merge para master

---

## Fluxos de Trabalho Críticos

### Pipeline de Build & Deploy

**Fluxo de Build do Pacote Lambda:**
1. Ponto de entrada: `scripts/build_lambda_package.sh`
2. Cria diretório `scripts/package/` (ou utiliza existente)
3. Instala dependências Python de `src/lambda_requirements.txt` no diretório de pacote
4. Copia `src/lambda_function.py` para o diretório de pacote
5. Compacta o pacote inteiro como `infraestructure/lambda_function_payload.zip`
6. Terraform referencia este arquivo ZIP durante o deployment

**Comandos principais:**
```bash
sh scripts/build_lambda_package.sh  # Constrói o pacote de deployment da lambda
cd infraestructure && terraform init && terraform apply  # Deploy da infraestrutura
```

**Workflows:**
- `workflows/deploy.yaml`: Executa em merge para master - constrói pacote, valida Terraform, aplica mudanças
- `workflows/test.yaml`: Executa em PRs - valida Terraform sem aplicar
- Ambos os workflows requerem credenciais AWS via secrets do GitHub: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

---

## Estrutura de Diretórios & Responsabilidades

| Caminho | Propósito |
|---------|-----------|
| `src/lambda_function.py` | Handler Lambda - contém função `handler(event, context)` que orquestra o fluxo de trabalho EMR |
| `src/lambda_requirements.txt` | Dependências Python para tempo de execução da Lambda |
| `scripts/build_lambda_package.sh` | Automação de build para artefato de deployment da Lambda |
| `infraestructure/` | Terraform Infrastructure as Code para recursos AWS |
| `infraestructure/provider.tf` | Configuração do provedor AWS + configuração de estado remoto em S3 (bucket: `00-terraform-state`) |
| `infraestructure/variables.tf` | Entradas configuráveis (região AWS, nome da Lambda, IDs de VPC/subnet, key pair) |
| `infraestructure/lambda.tf` | Recurso de função Lambda (handler: `lambda_function.handler`, memória: 128MB, timeout: 30s) |
| `infraestructure/iam.tf` | Roles e políticas IAM para Lambda (CloudWatch Logs, S3, permissões EMR) |

---

## Padrão de Função Lambda

**Assinatura:** `def handler(event, context)` em [src/lambda_function.py](../src/lambda_function.py)

**Responsabilidades:**
- Inicializa cliente boto3 EMR para região `us-east-1`
- Chama `client.run_job_flow()` para criar cluster EMR com:
  - **Nós Master/Core:** instâncias m5.xlarge usando preço SPOT
  - **Aplicações:** Spark, Hive, Pig, Hue, JupyterHub, Livy
  - **Configuração Spark:** Suporte Delta Lake, serialização Kryo, execução adaptativa de queries habilitada
  - **Steps:** Orquestra jobs Spark sequenciais (atualmente: Delta insert → Delta upsert)
  
**Formato de retorno:**
```python
{
    'statusCode': 200,
    'body': f"Started job flow {cluster_id['JobFlowId']}"
}
```

**Importante:** Lambda lê valores hardcoded para nomes de clusters, roles IAM, caminhos S3 e definições de steps. Modificações requerem reconstrução do pacote de deployment via `scripts/build_lambda_package.sh`.

---

## Padrões de Infrastructure-as-Code

### Gerenciamento de Estado do Terraform
- Estado remoto armazenado em bucket S3 `00-terraform-state` com chave `state/terraform.tfstate`
- `use_lockfile = true` previne modificações concorrentes
- Todas as variáveis possuem valores padrão (veja `infraestructure/variables.tf`)

### Convenção de Nomenclatura de Recursos
- Role/policy Lambda: `thiago-lambda-role`, `thiago-lambda-policy`
- Função Lambda: `thiagoexecutaEMRaovivo` (configurável via variável `lambda_function_name`)
- Todos os recursos tagueados com `IES: IGTI, CURSO: EDC`

### Estratégia IAM
Permissões da role Lambda incluem:
- **CloudWatch Logs:** Acesso total de escrita (debugging, monitoramento)
- **S3:** Acesso total (leitura de código Spark, escrita/leitura de logs e dados)
- **EMR:** Executar fluxos de trabalho, gerenciar clusters e instâncias
- **IAM:** Passar roles de serviço para EMR (`EMR_DefaultRole`, `EMR_EC2_DefaultRole`)

---

## Dados & Dependências Externas

**Caminhos S3 Críticos (hardcoded na Lambda):**
- Logs: `s3://datalake-test-thiago/99-logs/`
- Código Spark: `s3://datalake-test-thiago/98-codes/emr-code/pyspark/`

**Detalhes de Configuração EMR:**
- Release: `emr-7.2.0`
- Hive usa AWS Glue Data Catalog como metastore
- Spark configurado com Delta Lake 1.0.0 (`io.delta:delta-core_2.12`)
- Rede: Utiliza VPC predefinida (`vpc-d724b4bc`), subnet (`subnet-1df20360`), key pair EC2 (`thiago-teste`)

**Runtime Python:** Python 3.8 (linguagem do handler Lambda)

---

## Modificações Comuns

**Atualizar lógica da Lambda:**
1. Edite `src/lambda_function.py`
2. Execute `sh scripts/build_lambda_package.sh` para regenerar ZIP
3. Execute Terraform apply (redeploy automático via GitHub Actions no master)

**Adicionar dependências Python:**
1. Atualize `src/lambda_requirements.txt`
2. Reconstrua o pacote via script (pip install buscará no diretório `scripts/package/`)

**Alterar infraestrutura AWS:**
1. Modifique arquivos `infraestructure/*.tf`
2. Commit e push - GitHub Actions valida e aplica automaticamente

**Debugar job EMR falho:**
- Verifique logs do cluster EMR em `s3://datalake-test-thiago/99-logs/`
- Monitore Lambda via CloudWatch Logs (política IAM concede acesso)
- Verifique permissões de instância EC2 e configuração de step Spark

---

## Armadilhas & Notas Importantes

1. **Erro de digitação no nome do diretório:** `infraestructure/` (grafia em espanhol, não inglês `infrastructure/`)
2. **Credenciais & caminhos hardcoded:** Buckets S3, IDs de VPC, IDs de subnet, nomes de roles IAM estão hardcoded na Lambda e variáveis - sem injeção de variáveis de ambiente atualmente
3. **Travamento de estado Terraform:** Backend S3 utiliza lockfile - garanta que `use_lockfile = true` permaneça para deployments em equipe
4. **Dependências de roles EMR:** Lambda espera que `EMR_DefaultRole` e `EMR_EC2_DefaultRole` já existam na conta AWS (não criadas por este código)
5. **Dependência de arquivo ZIP:** Terraform referencia diretamente `lambda_function_payload.zip` - build deve executar antes de apply
