# tests/integration/test_emr_integration.py

from unittest.mock import patch, MagicMock
from lambda_function import handler


@patch("lambda_function.boto3.client")
def test_emr_integration(mock_boto_client):
    mock_emr = MagicMock()
    mock_boto_client.return_value = mock_emr

    mock_emr.run_job_flow.return_value = {
        "JobFlowId": "j-123456"
    }

    response = handler({}, {})

    assert response["statusCode"] == 200