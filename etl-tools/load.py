import argparse
from pathlib import Path
from core import TABLES, load_dump, VersionNotFound
from transform import upgrade


if __name__ == "__main__":
    THIS_FILE = Path(__file__)
    parser = argparse.ArgumentParser(
        prog=f"py {THIS_FILE.name}",
        description="Load a datadump into a table, applying the necessary transformations to migrate.",
    )

    parser.add_argument("filename")
    parser.add_argument("target_table", choices=TABLES)
    parser.add_argument(
        "-v",
        "--targetversion",
        type=int,
        help="Specify target version. Used only when target table doesn't have one (e.g. with fresh tables) ",
    )
    args = parser.parse_args()

    print("Reading", args.filename)
    dump = load_dump(args.filename)

    target_table = TABLES[args.target_table]
    try:
        target_version = target_table.version
    except VersionNotFound:
        if not args.targetversion:
            raise VersionNotFound(
                f"Target table {target_table.name} has no version information. Provide manually with -v {{num}}"
            )

        target_version = int(args.targetversion)

    print("Applying transformations")
    new_data = upgrade(dump, target_version)

    print("Loading to", target_table.name)
    target_table.populate(new_data)
