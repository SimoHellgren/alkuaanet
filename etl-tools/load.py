from functools import reduce
import json
from core import Table
from transform import v1_to_v2


def compose(*funcs):
    return reduce(lambda f, g: lambda x: f(g(x)), funcs)


# should move to core, probably
TABLES = {
    "songs": Table("songs", 1),
    "songs_v2": Table("songs_v2", 2),
}


transformations = {
    1: v1_to_v2,
}

if __name__ == "__main__":
    filename = ""
    with open(filename) as f:
        data = json.load(f)

    dump_version = data["__meta"]["table_version"]
    target_version = 2

    # get the needed transformations to bring data to the target version
    needed_transformations = [
        transformations.get(i) for i in range(dump_version, target_version)
    ]

    new_data = compose(*needed_transformations)(data)

    # TODO: edit data to correct data types (e.g. binary, decimal)
