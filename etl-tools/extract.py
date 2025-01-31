import argparse
from datetime import datetime
from pathlib import Path

from core import TABLES


if __name__ == "__main__":
    THIS_FILE = Path(__file__)
    parser = argparse.ArgumentParser(
        prog=f"py {THIS_FILE.name}",
        description="Given a table name, dumps the data. Tables need to be registered in core.py.",
    )

    parser.add_argument("table_name", choices=TABLES)
    args = parser.parse_args()

    table = TABLES[args.table_name]

    TARGET_FOLDER = THIS_FILE.parent / "dumps"
    TARGET_FOLDER.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    FILE = TARGET_FOLDER / f"{table.name}_{timestamp}.json"

    table.dump(FILE)
