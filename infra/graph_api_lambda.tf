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

data "aws_iam_policy_document" "dynamodb_access" {
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
      aws_dynamodb_table.a-test-table.arn,
      "${aws_dynamodb_table.a-test-table.arn}/index/*" # access to indices, too
    ]
  }

  # logging
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"] # might this be problematic?
  }
}

resource "aws_iam_policy" "dynamodb_policy" {
  name   = "DynamoDB-policy"
  policy = data.aws_iam_policy_document.dynamodb_access.json
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy_attachment" "graph_api_lambda_iam_attachment" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.dynamodb_policy.arn
}

data "archive_file" "graph_api_lambda_payload" {
  type        = "zip"
  source_dir  = "${path.module}/../graph/"
  excludes    = ["deps"] # this can be removed after lambda_layer deploy is automated, and the folder is cleaned up
  output_path = "${path.module}/managed-files/graph_lambda_payload.zip"
}

resource "aws_lambda_function" "graph_api_lambda" {
  filename      = "${path.module}/managed-files/graph_lambda_payload.zip"
  function_name = "alkuaanet-graph-api"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "schema.handler"

  source_code_hash = data.archive_file.graph_api_lambda_payload.output_base64sha256

  layers = [aws_lambda_layer_version.lambda_layer.arn]

  runtime = "python3.11"
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