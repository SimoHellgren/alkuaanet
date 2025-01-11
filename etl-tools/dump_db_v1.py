from datetime import datetime
import json
from pathlib import Path
from core import TABLES, sorted_groupby, JSONEncoder

TABLE = TABLES["songs"]


def kind(record: dict) -> str:
    if "type" in record:
        return record["type"]

    pk = record["pk"]

    if pk == "sequence":
        return "sequence"


if __name__ == "__main__":
    TARGET_FOLDER = Path(__file__).parent / "dumps"
    TARGET_FOLDER.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    FILE = TARGET_FOLDER / f"{TABLE.name}_{timestamp}.json"

    data = {k: list(v) for k, v in sorted_groupby(TABLE.get_data(), key=kind)}

    for k, records in data.items():
        print(f"Found {len(records):>4} records of kind {k}")

    print(f"Total {sum(map(len, data.values())):>4} records")

    data["__meta"] = {
        "table_name": TABLE.name,
        "table_version": TABLE.version,
    }

    with open(FILE, "w") as f:
        json.dump(data, f, cls=JSONEncoder)
