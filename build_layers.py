"""Utility for building lambda layers"""

import argparse
import sys
import subprocess
from pathlib import Path
import shutil
import logging

log = logging.getLogger()
log.setLevel(logging.INFO)

formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s")

handler = logging.StreamHandler()
handler.setFormatter(formatter)
log.addHandler(handler)

GROUPS = [
    "graph",
    "telegram",
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="py build_layers.py",
        description="Build lambda layers",
    )

    parser.add_argument("groups", choices=GROUPS, nargs="+")
    args = parser.parse_args()
    groups = args.groups

    OUT_FOLDER = Path("infra/managed-files")

    for group in groups:
        log.info(f"Handling group '{group}'")

        DEPS_FOLDER = Path("infra/python-layers") / group
        OUT_FILE = f"{group}_lambda_layer"  # no .zip here because of how shutil works

        log.info("Exporting requirements")

        # add folder and .gitignore if running for first time
        if not DEPS_FOLDER.exists():
            DEPS_FOLDER.mkdir(exist_ok=True, parents=True)
            with open(DEPS_FOLDER / ".gitignore", "w") as f:
                f.write("*\n")

        # update requirements
        subprocess.run(
            [
                "poetry",
                "export",
                "--only",
                group,
                "--without-hashes",
                "-o",
                DEPS_FOLDER / "requirements.txt",
            ]
        )

        log.info("Cleanup installation folder")

        # cleanup folder
        if (DEPS_FOLDER / "python").exists():
            shutil.rmtree(DEPS_FOLDER / "python")

        log.info("Installing dependencies")

        # install into folder
        subprocess.run(
            [
                "pip",
                "install",
                "-r",
                DEPS_FOLDER / "requirements.txt",
                "-t",
                DEPS_FOLDER / "python",
                "--upgrade",
                "--platform",
                "manylinux2014_x86_64",
                "--only-binary",
                ":all:",
            ]
        )

        log.info("Creating zipfile")

        # create zip
        file = shutil.make_archive(OUT_FOLDER / OUT_FILE, "zip", DEPS_FOLDER, "python")

        log.info(f"Finished creating {file}")
