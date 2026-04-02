# Importa a biblioteca boto3 para interagir com os serviços AWS
import boto3

def handler(event, context):
    """
    Lambda function that starts a job flow in EMR.
    """
    # Cria um cliente EMR para gerenciar clusters na região us-east-1
    client = boto3.client('emr', region_name='us-east-1')

    # Inicia um novo cluster EMR com configurações específicas
    cluster_id = client.run_job_flow(
                # Nome identificador do cluster
                Name='EMR-thiago-teste',
                # IAM roles para o serviço EMR e para instâncias EC2
                ServiceRole='EMR_DefaultRole',
                JobFlowRole='EMR_EC2_DefaultRole',
                VisibleToAllUsers=True,
                # Caminho S3 para armazenar logs de execução
                LogUri='s3://datalake-test-thiago/99-logs/',
                # Versão do EMR a ser utilizada
                ReleaseLabel='emr-7.2.0',
                # Configuração de instâncias EC2 do cluster
                Instances={
                    'InstanceGroups': [
                        # Nó Master - responsável por orquestrar as tarefas
                        {
                            'Name': 'Master nodes',
                            'Market': 'SPOT',  # Usa instâncias SPOT para reduzir custos
                            'InstanceRole': 'MASTER',
                            'InstanceType': 'm5.xlarge',  # Tipo de máquina
                            'InstanceCount': 1,
                        },
                        # Nós Worker - executam as tarefas de processamento
                        {
                            'Name': 'Worker nodes',
                            'Market': 'SPOT',
                            'InstanceRole': 'CORE',
                            'InstanceType': 'm5.xlarge',
                            'InstanceCount': 1,
                        }
                    ],
                    'Ec2KeyName': 'thiago-teste',  # Chave SSH para acessar as instâncias
                    'KeepJobFlowAliveWhenNoSteps': True,  # Mantém cluster ativo após conclusão dos steps
                    'TerminationProtected': False,  # Permite finalizar o cluster
                    'Ec2SubnetId': 'subnet-1df20360'  # VPC subnet específica
                },

                # Aplicações a serem instaladas no cluster
                Applications=[
                    {'Name': 'Spark'},  # Motor de processamento distribuído
                    {'Name': 'Hive'},  # SQL distribuído
                    {'Name': 'Pig'},  # Linguagem de análise de dados
                    {'Name': 'Hue'},  # Interface web para gerenciar dados
                    {'Name': 'JupyterHub'},  # Notebooks Jupyter
                    {'Name': 'JupyterEnterpriseGateway'},  # Gateway para Jupyter
                    {'Name': 'Livy'},  # API REST para Spark
                ],

                # Configurações customizadas do Spark e ambiente
                Configurations=[{
                    # Variáveis de ambiente do Spark
                    "Classification": "spark-env",
                    "Properties": {},
                    "Configurations": [{
                        "Classification": "export",
                        # Define Python 3 como interpretador padrão para PySpark
                        "Properties": {
                            "PYSPARK_PYTHON": "/usr/bin/python3",
                            "PYSPARK_DRIVER_PYTHON": "/usr/bin/python3"
                        }
                    }]
                },
                    # Integração com AWS Glue Catalog para metastore do Hive
                    {
                        "Classification": "spark-hive-site",
                        # Configura Hive para usar AWS Glue como catálogo de metadados
                        "Properties": {
                            "hive.metastore.client.factory.class": "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"
                        }
                    },
                    # Otimizações padrão do Spark
                    {
                        "Classification": "spark-defaults",
                        "Properties": {
                            "spark.submit.deployMode": "cluster",  # Modo cluster para melhor performance
                            "spark.speculation": "false",  # Desativa execução especulativa
                            "spark.sql.adaptive.enabled": "true",  # Otimização adaptativa de SQL
                            "spark.serializer": "org.apache.spark.serializer.KryoSerializer"  # Serialização mais rápida
                        }
                    },
                    # Aloca recursos máximos disponíveis do cluster para Spark
                    {
                        "Classification": "spark",
                        "Properties": {
                            "maximizeResourceAllocation": "true"
                        }
                    }
                ],
                
                # Define quantos steps podem executar em paralelo (1 = sequencial)
                StepConcurrencyLevel=1,
                
                # Lista de etapas (steps) a serem executadas no cluster
                Steps=[{
                    # Primeiro step: Inserção de dados com Delta Lake
                    'Name': 'Delta Insert do ENEM',
                    'ActionOnFailure': 'CONTINUE',  # Continua mesmo se este step falhar
                    'HadoopJarStep': {
                        'Jar': 'command-runner.jar',  # JAR executor de comandos
                        'Args': ['spark-submit',
                                 '--packages', 'io.delta:delta-core_2.12:1.0.0',  # Biblioteca Delta Lake
                                 '--conf', 'spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension', 
                                 '--conf', 'spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog', 
                                 '--master', 'yarn',  # Gerenciador de cluster
                                 '--deploy-mode', 'cluster',  # Executa no cluster
                                 's3://datalake-test-thiago/98-codes/emr-code/pyspark/01_delta_spark_insert.py'  # Script PySpark
                                 ]
                    }
                },
                # Segundo step: Simulação e UPSERT (atualização/inserção) de dados
                {
                    'Name': 'Simulacao e UPSERT do ENEM',
                    'ActionOnFailure': 'CONTINUE',  # Continua mesmo se este step falhar
                    'HadoopJarStep': {
                        'Jar': 'command-runner.jar',
                        'Args': ['spark-submit',
                                 '--packages', 'io.delta:delta-core_2.12:1.0.0',  # Biblioteca Delta Lake
                                 '--conf', 'spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension', 
                                 '--conf', 'spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog', 
                                 '--master', 'yarn',  # Gerenciador de cluster
                                 '--deploy-mode', 'cluster',  # Executa no cluster
                                 's3://datalake-test-thiago/98-codes/emr-code/pyspark/02_delta_spark_upsert.py'  # Script PySpark
                                 ]
                    }
                }],
            )
    
    # Retorna sucesso com o ID do cluster criado
    return {
        'statusCode': 200,
        'body': f"Started job flow {cluster_id['JobFlowId']}"
    }