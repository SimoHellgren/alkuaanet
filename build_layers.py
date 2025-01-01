"""Utility for building lambda layers"""

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


OUT_FOLDER = Path("infra/managed-files")

for group in ("graph", "telegram"):

    log.info(f"Handling group '{group}'")

    DEPS_FOLDER = Path(group) / "deps"
    OUT_FILE = f"{group}_lambda_layer"  # no .zip here because of how shutil works

    log.info("Exporting requirements")

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
        ]
    )

    log.info("Creating zipfile")

    # create zip
    file = shutil.make_archive(OUT_FOLDER / OUT_FILE, "zip", DEPS_FOLDER, "python")

    log.info(f"Finished creating {file}")
