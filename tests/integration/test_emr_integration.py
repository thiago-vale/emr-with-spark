# tests/integration/test_emr_integration.py

import boto3
from lambda_function import handler
from moto import mock_emr

@mock_emr
def test_emr_integration():
    client = boto3.client("emr", region_name="us-east-1")

    # Executa a lambda
    response = handler({}, {})

    assert response["statusCode"] == 200