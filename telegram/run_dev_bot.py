import os
from dotenv import load_dotenv
from app import build_app

if __name__ == "__main__":
    import os
    from time import sleep
    from dotenv import load_dotenv

    load_dotenv(override=True)

    TOKEN = os.environ.get("DEV_BOT_TOKEN")

    app = build_app(TOKEN)

    max_update = -1
    print("Running...")
    while True:
        updates = (
            app.bot.get_updates(params={"offset": max_update + 1})
            .json()
            .get("result", [])
        )

        for update in updates:
            print("processing", update)
            app.process_update(update)

        if updates:
            max_update = max(u["update_id"] for u in updates)

        sleep(1)
