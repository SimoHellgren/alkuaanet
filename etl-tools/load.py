import argparse
from decimal import Decimal
from pathlib import Path
import json
from core import TABLES, flatten, compose
from transform import v1_to_v2


def load_dump(file: Path):
    with open(file) as f:
        # parse numbers to Decimal, because that is what DynamoDB wants
        data = json.load(f, parse_float=Decimal, parse_int=Decimal)

    return data


transformations = {
    1: v1_to_v2,
}

if __name__ == "__main__":
    THIS_FILE = Path(__file__)
    parser = argparse.ArgumentParser(
        prog=f"py {THIS_FILE.name}",
        description="Load a datadump into a table, applying the necessary transformations to migrate.",
    )

    parser.add_argument("filename")
    parser.add_argument("target_table", choices=TABLES.keys())
    args = parser.parse_args()

    data = load_dump(args.filename)
    dump_version = int(data["__meta"]["table_version"])

    target_table = TABLES[args.target_table]
    target_version = target_table.version

    # get the needed transformations to bring data to the target version
    needed_transformations = [
        transformations.get(i) for i in range(dump_version, target_version)
    ]

    new_data = compose(*needed_transformations)(data)

    print(
        f"Migrating from version {dump_version} to table {target_table.name}, version {target_version}"
    )

    data_in = list(flatten((vals for k, vals in new_data.items() if k != "__meta")))

    target_table.populate(data_in)
