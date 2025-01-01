data "archive_file" "telegram_bot_lambda_payload" {
  type        = "zip"
  source_dir  = "${path.module}/../telegram/"
  output_path = "${path.module}/managed-files/telegram_lambda_payload.zip"
  excludes    = ["deps", "__pycache__"]
}

resource "aws_lambda_function" "telegram_bot_lambda" {
  filename      = "${path.module}/managed-files/telegram_lambda_payload.zip"
  function_name = "alkuaanet-telegram-bot"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "lambda_function.handler"

  source_code_hash = data.archive_file.telegram_bot_lambda_payload.output_base64sha256

  layers = [aws_lambda_layer_version.telegram_bot_lambda_layer.arn]

  environment {
    variables = {
      API_URL = aws_lambda_function_url.graph_api_lambda_url.function_url
    }
  }

  runtime = "python3.11"
}

resource "aws_lambda_function_url" "telegram_bot_lambda_url" {
  function_name      = aws_lambda_function.telegram_bot_lambda.function_name
  authorization_type = "NONE"
}

resource "aws_cloudwatch_log_group" "telegram_bot_log_group" {
  name = "/aws/lambda/${aws_lambda_function.telegram_bot_lambda.function_name}"
  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_ssm_parameter" "telegram_bot_token" {
  name  = "alkuaanet-telegram-bot-token"
  type  = "SecureString"
  value = " "

  lifecycle {
    ignore_changes = [value]
  }
}
