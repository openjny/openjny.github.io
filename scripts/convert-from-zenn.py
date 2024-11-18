#!/bin/env python3
# zenn の markdown ファイルを処理するスクリプト
import argparse
import sys
import re


def convert(filename):
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # 解析
    for i, line in enumerate(lines):
        if re.match(r"^:::[a-zA-Z]+$", line):
            parameter = re.match(r":::(.*)", line).group(1)
            lines[i] = "{{< notice info >}}\n"
        elif re.match(r"^:::$", line):
            lines[i] = "{{< /notice >}}\n"
        elif re.match(r"^!\[.*\]\(.*\)", line):
            alt = re.match(r"!\[(.*)\]\(.*\)", line).group(1)
            url = re.match(r"!\[.*\]\((.*)\)", line).group(1)
            caption = ""
            if re.match(r"\*.+\*", lines[i + 1]):
                caption = re.match(r"\*(.*)\*", lines[i + 1]).group(1)
                lines[i + 1] = "\n"

            lines[i] = (
                '{{< figure src="' + url + '" caption="' + caption.strip() + '" >}}\n'
            )

    try:
        with open(filename, "w") as f:
            prev_empty = True
            for line in lines:
                is_empty = re.match(r"^\s*$", line)
                if prev_empty and is_empty:
                    continue
                f.write(line)
                prev_empty = is_empty
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # 引数の取得 (第一引数がファイル名)
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to the markdown file to process.")
    args = parser.parse_args()

    convert(args.file)
