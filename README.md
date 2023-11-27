# alkuaanet

Starting notes of songs. A Telegram bot calling a GraphQL API sitting on top of a DynamoDB table.

Lambda layers are not automatically built.

Manual steps:
1. Store the Telegram bot's token in SSM after it has been created (by terraform)
2. Set up a [webhook](https://core.telegram.org/bots/api#setwebhook) to the bot's function url
