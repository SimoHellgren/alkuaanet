# alkuaanet

Starting notes of songs. A Telegram bot calling a GraphQL API sitting on top of a DynamoDB table.

You'll need:
* a `config.py` in the [telegram](telegram) folder defining:
  * `token` - a Telegram Bot token
  * `apiurl` - the address of the backend

You'll also need `opusenc` in order to create opus-files when posting / putting songs.
