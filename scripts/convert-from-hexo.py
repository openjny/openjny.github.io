#!/bin/env python3
# hexo の markdown ファイルを処理するスクリプト
import argparse
import sys
import re


def convert(path):
    # get filename only (basename)
    filename = path.split("/")[-1]

    # filename := "YYYY-MM-DD-slug.md"
    result = re.match(r"(\d{4}-\d{2}-\d{2})-(.*).md", filename)
    if not result:
        print("Error: Invalid filename.", file=sys.stderr)
        sys.exit(1)

    metadata = {
        "date": result.group(1),
        "slug": result.group(2),
    }

    try:
        with open(path, "r") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(metadata)

    contents = ""
    STATE_NORMAL = 0
    STATE_CODE = 1
    state = STATE_NORMAL
    for i, line in enumerate(lines):
        # state management
        if re.match(r"^```", line):
            if state == STATE_NORMAL:
                state = STATE_CODE
            else:
                state = STATE_NORMAL

        # quote
        if state != STATE_NORMAL:
            contents += line
            continue

        # metadata: slug
        if re.match(r"^title:", line):
            line += f"slug: {metadata['slug']}\n"
        elif re.match(r"^slug:", line):
            line = ""
        # metadata: date
        elif re.match(r"^date:", line):
            line = f"date: {metadata['date']}\n"
        # metadata: category
        elif re.match(r"^category:", line):
            category = re.match(r"category:(.*)", line).group(1).strip()
            line = f"categories:\n  - {category}\n"
        # 画像
        elif re.match(r"^!\[.*\]\(.*\)", line):
            alt, url = re.match(r"!\[(.*)\]\((.*)\)", line).groups()
            if url.startswith("./"):
                url = url[2:]
            line = '{{< figure src="' + url + '" caption="' + alt.strip() + '" >}}\n'
        # <!--more-->
        elif re.match(r"<!--\s*more\s*-->", line):
            line = "## <!--more-->\n"
        # [[toc]]
        elif re.match(r"\[\[toc\]\]", line):
            line = ""
        # :::
        elif re.match(r"^:::.+", line):
            parameter = re.match(r":::(.*)", line).group(1)
            line = "{{< notice info >}}\n"
        elif re.match(r"^:::$", line):
            line = "{{< /notice >}}\n"

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
