terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5"
    }

    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3"
    }
  }
}

provider "aws" {
  region = "eu-west-1"
}
