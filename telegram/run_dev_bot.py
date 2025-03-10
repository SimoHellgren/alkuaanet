import os
from time import sleep

from app import build_app
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv(override=True)

    TOKEN = os.environ.get("DEV_BOT_TOKEN", "")

    app = build_app(TOKEN)

    max_update = -1
    print("Running...")  # noqa: T201
    while True:
        updates = (
            app.get_updates(params={"offset": max_update + 1}).json().get("result", [])
        )

        for update in updates:
            print("processing", update)  # noqa: T201
            app.process_update(update)

        if updates:
            max_update = max(u["update_id"] for u in updates)

        sleep(1)
