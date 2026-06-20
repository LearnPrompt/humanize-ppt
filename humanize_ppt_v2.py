#!/usr/bin/env python3
"""Compatibility module for `python3 -m humanize_ppt_v2`.

The implementation lives in scripts/humanize_ppt_v2.py; this wrapper keeps the
backlog command usable from the repository root without duplicating logic.
"""

from scripts.humanize_ppt_v2 import main


if __name__ == "__main__":
    import sys

    sys.exit(main())
