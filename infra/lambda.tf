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

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}


data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = "${path.module}/../graph/"
  excludes    = ["deps", "schema.py"]
  output_path = "${path.module}/managed-files/lambda_payload.zip"
}

resource "aws_lambda_function" "test_lambda" {
  filename      = "${path.module}/managed-files/lambda_payload.zip"
  function_name = "tf_lambda"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "lambda_function.lambda_handler"

  source_code_hash = data.archive_file.lambda.output_base64sha256

  runtime = "python3.11"
}
