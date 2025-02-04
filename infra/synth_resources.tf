resource "aws_ecr_repository" "alkuaani-synth" {
  name = "alkuaani-synth"
}

# authorization credential for ECR
data "aws_ecr_authorization_token" "token" {}

# hacky hack for building and pushing docker image
provider "docker" {
  registry_auth {
    address  = data.aws_ecr_authorization_token.token.proxy_endpoint
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}

# build image
resource "docker_image" "synth-image-local" {
  name = "${aws_ecr_repository.alkuaani-synth.repository_url}:latest"
  build {
    context = "${path.module}/../synth"
  }

  platform = "linux/amd64"

}

# push image to ecr repo
resource "docker_registry_image" "synth-image-ecr" {
  name = docker_image.synth-image-local.name
}


resource "aws_lambda_function" "alkuaanet-synth-lambda" {
  function_name = "alkuaanet-synth"
  memory_size   = 512
  role          = aws_iam_role.iam_for_lambda.arn
  timeout       = 5
  image_uri     = "${aws_ecr_repository.alkuaani-synth.repository_url}:latest"
  package_type  = "Image"
}

resource "aws_cloudwatch_log_group" "synth_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.alkuaanet-synth-lambda.function_name}"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}
