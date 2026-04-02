
resource "aws_cloudwatch_event_rule" "scheduled_rule" {
  name                = "emr-scheduled-trigger"
  description         = "Dispara Lambda diariamente às 1 AM (horário Brasil)"
  # Cron format: minuto hora dia mês dia_da_semana ano
  # 0 4 * * ? * = 04:00 UTC (02:00 Brasil) todos os dias
  schedule_expression = "cron(0 4 * * ? *)"
}

resource "aws_cloudwatch_event_target" "lambda_target_scheduled" {
  rule      = aws_cloudwatch_event_rule.scheduled_rule.name
  target_id = "ExecutaEMRLambda"
  arn       = aws_lambda_function.executa_emr.arn
}

# Permissão para EventBridge invocar a função Lambda
resource "aws_lambda_permission" "allow_eventbridge_scheduled" {
  statement_id  = "AllowExecutionFromEventBridgeScheduled"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.executa_emr.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scheduled_rule.arn
}

