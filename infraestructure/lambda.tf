resource "aws_lambda_function" "executa_emr" {
  filename         = "${path.module}/lambda_function_payload.zip"
  function_name    = var.lambda_function_name
  role             = aws_iam_role.lambda.arn
  handler          = "lambda_function.handler"
  memory_size      = 512
  timeout          = 60
  source_code_hash = filebase64sha256("${path.module}/lambda_function_payload.zip")

  runtime = "python3.11"

  tags = {
    IES   = "IGTI"
    CURSO = "EDC"
  }

}