# alkuaanet

Starting notes of songs. FastAPI backend with SQLAlchemy and a Telegram bot.

You'll need:
* a `config.py` in the [backend/app](backend/app) folder defining:
  * `DB_URI` - a URI to connect to the database (anything compatible with SQLAlchemy)
  * `TEST_DB_URI` - if you want to run tests
* a `config.py` in the [telegram](telegram) folder defining:
  * `token` - a Telegram Bot token
  * `apiurl` - the address of the backend

You'll also need `opusenc` in order to create opus-files when posting / putting songs.

Start the backend with `uvicorn backend.app.main:app`
