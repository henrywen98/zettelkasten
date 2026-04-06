#!/usr/bin/env python3
"""Rewrite image/attachment links in markdown files to point to a new assets/ directory.

Usage: uv run relink.py <md_file> <old_base> <new_base>
Example: uv run relink.py note.md "img/" "../assets/"

Can also be imported as a module: from relink import relink_content
"""

import re
import sys
from pathlib import Path


def relink_content(content: str, path_map: dict[str, str]) -> str:
    """Replace paths in content according to path_map.

    path_map: {"old/path/img.png": "assets/img.png", ...}
    Handles two formats:
      - ![alt](old/path/img.png) → ![alt](assets/img.png)
      - ![[old/path/img.png]] → ![[assets/img.png]]
    """
    def replace_md(m: re.Match) -> str:
        alt = m.group(1)
        old_path = m.group(2)
        new_path = path_map.get(old_path)
        if not new_path:
            basename = Path(old_path).name
            new_path = path_map.get(basename, old_path)
        return f"![{alt}]({new_path})"

    def replace_wiki(m: re.Match) -> str:
        old_path = m.group(1)
        new_path = path_map.get(old_path)
        if not new_path:
            basename = Path(old_path).name
            new_path = path_map.get(basename, old_path)
        return f"![[{new_path}]]"

    content = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_md, content)
    content = re.sub(r"!\[\[([^\]]+)\]\]", replace_wiki, content)
    return content


def main():
    if len(sys.argv) < 4:
        print("Usage: uv run relink.py <md_file> <old_prefix> <new_prefix>")
        sys.exit(1)

    md_file = Path(sys.argv[1])
    old_prefix = sys.argv[2]
    new_prefix = sys.argv[3]

    content = md_file.read_text(encoding="utf-8")

    path_map = {}
    for m in re.finditer(r"!\[.*?\]\((.+?)\)", content):
        old = m.group(1)
        if old.startswith(old_prefix):
            path_map[old] = old.replace(old_prefix, new_prefix, 1)
    for m in re.finditer(r"!\[\[(.+?)\]\]", content):
        old = m.group(1)
        if old.startswith(old_prefix):
            path_map[old] = old.replace(old_prefix, new_prefix, 1)

    new_content = relink_content(content, path_map)

    if new_content != content:
        md_file.write_text(new_content, encoding="utf-8")
        print(f"Relinked {len(path_map)} links: {md_file}")
    else:
        print(f"No changes needed: {md_file}")


if __name__ == "__main__":
    main()
