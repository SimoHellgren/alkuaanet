resource "aws_dynamodb_table" "a-test-table" {
  name         = "songs"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  range_key    = "sk"

  attribute {
    name = "pk"
    type = "S"
  }

  attribute {
    name = "sk"
    type = "S"
  }

  attribute {
    name = "type"
    type = "S"
  }

  global_secondary_index {
    name               = "LookupIndex"
    hash_key           = "type"
    range_key          = "sk"
    projection_type    = "INCLUDE"
    non_key_attributes = ["name"]
  }
}
