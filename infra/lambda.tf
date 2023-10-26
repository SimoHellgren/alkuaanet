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

resource "aws_iam_role_policy_attachment" "test-attach" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.dynamodb_policy.arn
}

data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = "${path.module}/../graph/"
  excludes    = ["deps"] # this can be removed after lambda_layer deploy is automated, and the folder is cleaned up
  output_path = "${path.module}/managed-files/lambda_payload.zip"
}

resource "aws_lambda_function" "test_lambda" {
  filename      = "${path.module}/managed-files/lambda_payload.zip"
  function_name = "tf_lambda"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "lambda_function.handler"

  source_code_hash = data.archive_file.lambda.output_base64sha256

  layers = [aws_lambda_layer_version.lambda_layer.arn]

  runtime = "python3.11"
}


resource "aws_cloudwatch_log_group" "function_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.test_lambda.function_name}"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}
