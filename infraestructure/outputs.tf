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

output "lambda_invocation_role_name" {
  description = "Nome da role IAM usada pela Lambda"
  value       = aws_iam_role.lambda.name
}
