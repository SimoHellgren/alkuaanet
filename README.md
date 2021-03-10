# alkuaanet

Starting notes of songs. FastAPI backend with SQLAlchemy and a Telegram bot.

You'll need:
* a `config.py` in the [backend/main](backend/main) folder defining:
  * `DB_URI` - a URI to connect to the database (anything compatible with SQLAlchemy)
* a `config.py` in the [telegram](telegram) folder defining:
  * `token` - a Telegram Bot token
  * `apiurl` - the address of the backend

You'll also need `opusenc` in order to create opus-files when posting / putting songs.

Start the backend with `uvicorn backend.main:app`
