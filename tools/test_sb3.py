#!/usr/bin/env python3
"""Entrada única a las regresiones del artefacto Scratch."""
from pathlib import Path
from validate_sb3 import run_all_tests

if __name__ == "__main__":
    for result in run_all_tests(str(Path(__file__).resolve().parents[1] / "NEXUS-BLOCKS-ENDLESS.sb3")):
        print(result)
