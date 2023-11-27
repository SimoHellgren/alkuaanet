data "archive_file" "telegram_bot_lambda_payload" {
  type        = "zip"
  source_dir  = "${path.module}/../telegram/"
  output_path = "${path.module}/managed-files/telegram_lambda_payload.zip"
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
  name              = "/aws/lambda/${aws_lambda_function.telegram_bot_lambda.function_name}"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}

data "aws_iam_policy_document" "telegram_bot_accesses" {
  # ssm
  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters"
    ]
    resources = [
      "arn:aws:ssm:eu-west-1:896979235420:parameter/alkuaanet-telegram-bot-token"
    ]
  }
}

resource "aws_iam_policy" "telegram_bot_policy" {
  name   = "telegram-bot-policy"
  policy = data.aws_iam_policy_document.telegram_bot_accesses.json
}

resource "aws_iam_role" "telegram_bot_role" {
  name               = "telegram-bot-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy_attachment" "telegram_bot_role_attachment" {
  role       = aws_iam_role.telegram_bot_role.name
  policy_arn = aws_iam_policy.telegram_bot_policy.arn
}
