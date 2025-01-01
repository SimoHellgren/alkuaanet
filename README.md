# alkuaanet

Starting notes of songs. A Telegram bot calling a GraphQL API sitting on top of a DynamoDB table.

How to get things up and running:
1. Acquire a bot token and store it in SSM after it has been created by Terraform
2. Build lambda layers for Telegram bot and API
   - run `py build_layers.py` (see [below](#building-lambda-layers) for a more detailed description) 
3. Set up a [webhook](https://core.telegram.org/bots/api#setwebhook) to the bot's function url
   - check the API's URL and set it as an environment variable `API_URL` and run `py set_webhook.py`
   - after this the bot should be functional!


## Building lambda layers
Terraform doesn't handle lambda layer building particularly well, so there's a utility script `build_layers.py` which:
1. Exports dependencies from poetry
2. `pip install`s the dependencies to gitignored folders
3. zips the folders

# Local testing
## Graph API
Run `uvicorn graph.schema:app` to start a local API instance (against production DB). 