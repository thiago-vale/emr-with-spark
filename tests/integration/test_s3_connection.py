import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def test_s3_connection():
    try:
        # Cria cliente S3 (usa credenciais configuradas no ambiente)
        s3 = boto3.client('s3')

        # Tenta listar buckets (boa forma de validar conexão)
        response = s3.list_buckets()

        print("✅ Conexão com S3 realizada com sucesso!\n")
        print("Buckets disponíveis:")

        for bucket in response['Buckets']:
            print(f"- {bucket['Name']}")

    except NoCredentialsError:
        print("❌ Credenciais não encontradas. Configure AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY.")
    
    except ClientError as e:
        print(f"❌ Erro ao conectar ao S3: {e}")

    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


if __name__ == "__main__":
    test_s3_connection()