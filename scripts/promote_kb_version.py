#!/usr/bin/env python3
"""Promote a validated KB version to live (docs/04 §4.5).

Usage: python scripts/promote_kb_version.py kb_v2
Refuses to promote a version that is not marked validated in the registry.
"""
from __future__ import annotations

import sys

from core.versioning import VersionRegistry


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: promote_kb_version.py <kb_vN>")
        return 2
    registry = VersionRegistry()
    try:
        registry.promote(argv[1])
    except (KeyError, ValueError) as exc:
        print(f"refused: {exc}")
        return 1
    print(f"promoted {argv[1]} to live")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
