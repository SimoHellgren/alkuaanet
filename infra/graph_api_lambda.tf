data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "alkuaanet_accesses" {
  # dynamodb
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:BatchGetItem",
      "dynamodb:GetItem",
      "dynamodb:Query",
      "dynamodb:Scan",
      "dynamodb:BatchWriteItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem"
    ]
    resources = [
      aws_dynamodb_table.songs-table.arn,
      "${aws_dynamodb_table.songs-table.arn}/index/*", # access to indices, too

      aws_dynamodb_table.songs-table-v2.arn,
      "${aws_dynamodb_table.songs-table-v2.arn}/index/*", # access to indices, too
    ]
  }

  # synth
  statement {
    effect = "Allow"
    actions = [
      "lambda:InvokeFunction"
    ]
    resources = [
      aws_lambda_function.alkuaanet-synth-lambda.arn
    ]
  }

  # ssm
  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters"
    ]
    resources = [
      aws_ssm_parameter.telegram_bot_token.arn,
      aws_ssm_parameter.fernet-key.arn
    ]
  }

  # logging
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_policy" "alkuaanet_policy" {
  name   = "Alkuaanet-Policy"
  policy = data.aws_iam_policy_document.alkuaanet_accesses.json
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy_attachment" "alkuaanet_lambda_policy_attachment" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.alkuaanet_policy.arn
}

data "archive_file" "graph_api_lambda_payload" {
  type        = "zip"
  source_dir  = "${path.module}/../graph/"
  excludes    = ["**/__pycache__", "README.md", "**/.mypy_cache"]
  output_path = "${path.module}/managed-files/graph_lambda_payload.zip"
}

resource "aws_lambda_function" "graph_api_lambda" {
  filename      = "${path.module}/managed-files/graph_lambda_payload.zip"
  function_name = "alkuaanet-graph-api"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "lib.schema.handler"
  timeout       = 5
  memory_size   = 512

  source_code_hash = data.archive_file.graph_api_lambda_payload.output_base64sha256

  layers = [aws_lambda_layer_version.graph_api_lambda_layer.arn]

  runtime = "python3.13"
}

resource "aws_lambda_function_url" "graph_api_lambda_url" {
  function_name      = aws_lambda_function.graph_api_lambda.function_name
  authorization_type = "NONE"
}

resource "aws_cloudwatch_log_group" "graph_api_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.graph_api_lambda.function_name}"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}


resource "aws_ssm_parameter" "fernet-key" {
  name  = "alkuaanet-fernet-key"
  type  = "SecureString"
  value = " "

  lifecycle {
    ignore_changes = [value]
  }
}
