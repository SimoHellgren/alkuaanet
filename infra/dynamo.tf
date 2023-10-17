resource "aws_dynamodb_table" "a-test-table" {
  name         = "songs"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"
  range_key    = "name"

  attribute {
    name = "id"
    type = "N"
  }

  attribute {
    name = "name"
    type = "S"
  }

}
