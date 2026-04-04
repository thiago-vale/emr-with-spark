from unittest.mock import patch, MagicMock
from lambda_function import handler


@patch("lambda_function.boto3.client")
def test_handler_success(mock_boto_client):
    # Cria um mock do cliente EMR
    mock_emr = MagicMock()
    mock_boto_client.return_value = mock_emr

    # Define o retorno fake do run_job_flow
    mock_emr.run_job_flow.return_value = {
        "JobFlowId": "j-123456"
    }

    # Executa a lambda
    response = handler({}, {})

    # Verificações
    assert response["statusCode"] == 200
    assert "j-123456" in response["body"]

    # Garante que o método foi chamado
    mock_emr.run_job_flow.assert_called_once()