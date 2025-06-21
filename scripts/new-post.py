import os
import sys
from datetime import datetime
import argparse
import re

TEMPLATE = '''+++
title = "{title}"
description = "{description}"
slug = "{slug}"
date = "{date}"
categories = [
    "Azure"
]
tags = [
    "SRE",
    "DevOps"
]
series = ["AI の運用を支える AIOps"]
keywords = ["Azure", "SRE"]
isCJKLanguage = {is_cjk}
+++

{body}
'''


def to_kebab_case(s):
    s = re.sub(r'[^a-zA-Z0-9_\s-]', '', s)
    s = s.replace('_', ' ')
    s = re.sub(r'\s+', '-', s)
    return s.lower()

def is_kebab_case(s):
    return re.fullmatch(r'[a-z0-9\-]+', s) is not None

def is_english_only(s):
    return re.fullmatch(r'[a-z0-9\-]+', s) is not None


def main():
    parser = argparse.ArgumentParser(description="Create a new post (multi-language or single-language)")
    parser.add_argument('slug', help='slug for the post (e.g. aiops-intro)')
    parser.add_argument('--single', action='store_true', help='Create single markdown file instead of multi-language')
    args = parser.parse_args()

    slug = args.slug
    if not is_english_only(slug):
        print(f"Error: Slug '{slug}' must be in English and kebab-case (e.g. aiops-intro).")
        sys.exit(1)
    if not is_kebab_case(slug):
        slug_input = slug
        slug = to_kebab_case(slug)
        print(f"Warning: Slug '{slug_input}' was converted to kebab-case: '{slug}'")

    post_date = datetime.now().strftime('%Y-%m-%d')
    posts_dir = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts')

    if args.single:
        ja_md = TEMPLATE.format(
            title="TODO: ここにタイトルを書いてください。",
            description="TODO: ここに説明文を書いてください。",
            slug=slug,
            date=post_date,
            is_cjk='true',
            body='TODO: ここに本文を書いてください。'
        )
        path = os.path.join(posts_dir, f'{post_date}-{slug}.md')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(ja_md)
        print(f'Created: {path}')

    else:
        folder = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts', f'{post_date}-{slug}')
        os.makedirs(folder, exist_ok=True)

        ja_md = TEMPLATE.format(
            title="TODO: ここにタイトルを書いてください。",
            description="TODO: ここに説明文を書いてください。",
            slug=slug,
            date=post_date,
            is_cjk='true',
            body='TODO: ここに本文を書いてください。'
        )
        with open(os.path.join(folder, 'index.ja.md'), 'w', encoding='utf-8') as f:
            f.write(ja_md)

        en_md = TEMPLATE.format(
            title="TODO: Write your title here.",
            description="TODO: Write your description here.",
            slug=slug,
            date=post_date,
            is_cjk='false',
            body='TODO: Write your content here.'
        )

        # en_md から isCJKLanguage 行を削除
        en_md_lines = en_md.splitlines()
        en_md_lines = [line for line in en_md_lines if not line.startswith('isCJKLanguage')]
        en_md = '\n'.join(en_md_lines) + '\n'

        with open(os.path.join(folder, 'index.en.md'), 'w', encoding='utf-8') as f:
            f.write(en_md)

        print(f'Created: {folder}/index.ja.md, index.en.md')


if __name__ == "__main__":
    main()
