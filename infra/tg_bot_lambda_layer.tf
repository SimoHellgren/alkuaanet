resource "aws_lambda_layer_version" "telegram_bot_lambda_layer" {
  filename         = "${path.module}/managed-files/telegram_lambda_layer.zip"
  layer_name       = "telegram-bot-deps"
  source_code_hash = filebase64sha256("${path.module}/managed-files/telegram_lambda_layer.zip")
  skip_destroy     = true

  compatible_runtimes      = ["python3.13"]
  compatible_architectures = ["x86_64"]
}
