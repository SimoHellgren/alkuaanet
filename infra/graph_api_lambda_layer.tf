resource "aws_lambda_layer_version" "graph_api_lambda_layer" {
  filename         = "${path.module}/managed-files/graph_lambda_layer.zip"
  layer_name       = "graphql-deps"
  source_code_hash = filebase64sha256("${path.module}/managed-files/graph_lambda_layer.zip")
  skip_destroy     = true

  compatible_runtimes = ["python3.11"]
}
