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
    context = "${path.module}/../backend"
  }

  platform = "linux/amd64"

}

# push image to ecr repo
resource "docker_registry_image" "synth-image-ecr" {
  name = docker_image.synth-image-local.name
}
