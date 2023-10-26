resource "aws_lambda_layer_version" "lambda_layer" {
  filename   = "${path.module}/managed-files/lambda_layer.zip"
  layer_name = "graphql-deps"

  compatible_runtimes = ["python3.11"]
}
