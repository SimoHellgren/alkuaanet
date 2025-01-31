import argparse
from datetime import datetime
from pathlib import Path
from core import load_dump
from transform import dump_version, kind_v1, kind_v2, kindify

KINDFUNCS = {
    1: kind_v1,
    2: kind_v2,
}

if __name__ == "__main__":
    script_name = Path(__file__).name
    parser = argparse.ArgumentParser(
        prog=f"py {script_name}",
        description="Show information about a dumpfile",
    )

    parser.add_argument("filename")
    args = parser.parse_args()

    file = Path(args.filename)
    dump = load_dump(file)

    version = dump_version(dump)
    kindfunc = KINDFUNCS[version]
    data = kindify(dump, kindfunc)

    tablename, time = file.stem.rsplit("_", 1)
    dt = datetime.strptime(time, "%Y-%m-%dT%H%M%S")

    print(f"Table `{tablename}` (version {version})")
    print(f"Extracted {dt}")
    print("Records:")
    for k, v in data.items():
        print(f"- {k:<10} {len(v):>4}")

    print(f"Total {len(dump)} records")
