#!/bin/env python3
import argparse
import sys
import re


def convert(path):
    try:
        with open(path, "r") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    contents = ""
    STATE_BEFORE = 0
    STATE_PROCESSING = 1
    STATE_DONE = 2
    state = STATE_BEFORE
    for line in lines:
        if state == STATE_BEFORE and re.match(r"^##\s+<!-+\s*more\s*--+>", line):
            state = STATE_PROCESSING
            continue
        elif state == STATE_PROCESSING and re.match(r"^##\s+.*", line):
            contents += line.rstrip() + " <!--more-->\n"
            state = STATE_DONE
            continue

        if state != STATE_PROCESSING:
            contents += line

    try:
        with open(path, "w") as f:
            f.write(contents)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to the markdown file to process.")
    args = parser.parse_args()

    convert(args.file)
