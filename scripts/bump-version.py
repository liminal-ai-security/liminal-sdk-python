#!/usr/bin/env python
"""Define a script to bump the release version."""

import argparse
from pathlib import Path

import tomli
import tomli_w

ARG_PARSER = argparse.ArgumentParser(description="Bump the release version.")
ARG_PARSER.add_argument("version", type=str, help="The version to bump to.")

PYPROJECT_FILEPATH = Path("pyproject.toml")


if __name__ == "__main__":
    args = ARG_PARSER.parse_args()
    with PYPROJECT_FILEPATH.open("rb") as file:
        pyproject_toml = tomli.load(file)

    pyproject_toml["project"]["version"] = args.version

    with PYPROJECT_FILEPATH.open("wb") as file:
        tomli_w.dump(pyproject_toml, file)
