#!/usr/bin/env python3
"""Start Candy Store Tycoon.  Options: --windowed, --version, --smoke-test <file>"""
import sys

from candystore.app import main

if __name__ == "__main__":
    sys.exit(main())
