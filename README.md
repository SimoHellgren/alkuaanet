# alkuaanet

Starting notes of songs. A Telegram bot calling a GraphQL API sitting on top of a DynamoDB table.

How to get things up and running:
1. Build lambda layers for Telegram bot and API
   - run `py build_layers.py` (see [below](#building-lambda-layers) for a more detailed description)
2. `cd infra && terraform apply` 
3. Set SSM parameters
   - acquire [Telegram bot token](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)
   - generate a secret to use as a key for Fernet (see e.g. [here](https://cryptography.io/en/latest/fernet/#cryptography.fernet.Fernet))
   - set the above mentioned to env vars `BOT_TOKEN` and `FERNET_KEY` and run `py set_ssm_parameters.py`
4. Generate a superuser token and add it to the DynamoDB table
   - you can use `generate_superuser_token.py` to create the token. Create record in DynamoDB with `pk=token, sk=superuser, value=<key>`
   - the type of `value` in DDB is binary, which only accepts base64 - the above mentioned script takes this into account, and prints out a base64-encoded value
5. Set up a [webhook](https://core.telegram.org/bots/api#setwebhook) to the bot's function url
   - check the API's URL and set it as an environment variable `API_URL` and run `py set_webhook.py`
     - you can do `terraform show aws_lambda_function_url.graph_api_lambda_url` to get the value
     - you could probably automate this with lambda somehow, too. 
   - after this the bot should be functional!


## Building lambda layers
Terraform doesn't handle lambda layer building particularly well, so there's a utility script `build_layers.py` which:
1. Exports dependencies from poetry
2. `pip install`s the dependencies to gitignored folders
3. zips the folders

This script is handy when doing version upgrades or adding new dependencies. Packaging everything with Docker might be a nicer option, though.

# Local testing
## Graph API
Run `uvicorn graph.lib.schema:app` to start a local API instance (against production DB). 
