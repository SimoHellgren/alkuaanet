resource "aws_dynamodb_table" "songs-table" {
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

resource "aws_dynamodb_table" "songs-table-v2" {
  name         = "songs_v2"
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
    name = "search_name"
    type = "S"
  }

  attribute {
    name = "random"
    type = "N"
  }

  local_secondary_index {
    name            = "search_index"
    range_key       = "search_name"
    projection_type = "ALL"
  }

  local_secondary_index {
    name            = "random_index"
    range_key       = "random"
    projection_type = "KEYS_ONLY"
  }

  global_secondary_index {
    name            = "reverse_index"
    hash_key        = "sk"
    range_key       = "pk"
    projection_type = "KEYS_ONLY"
  }
}
