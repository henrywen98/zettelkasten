#!/usr/bin/env python3
"""Scan an Obsidian vault and generate manifest.json.

Usage: uv run scan.py <vault_path> [output_path]
Output: manifest.json with metadata and preview for each md file
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

import frontmatter


def extract_date_from_filename(name: str) -> str | None:
    """Extract date from filename, e.g. '20260114-2042-xxx.md' → '2026-01-14'"""
    m = re.match(r"(\d{4})(\d{2})(\d{2})", name)
    if m:
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 2000 <= year <= 2099 and 1 <= month <= 12 and 1 <= day <= 31:
            return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None


def extract_images(content: str) -> list[str]:
    """Extract image references in both markdown and Obsidian formats"""
    patterns = [
        r"!\[.*?\]\((.+?)\)",        # ![alt](path)
        r"!\[\[(.+?)\]\]",           # ![[path]]
    ]
    images = []
    for p in patterns:
        images.extend(re.findall(p, content))
    return images


def count_words(text: str) -> int:
    """Word count for mixed CJK and English text"""
    chinese = len(re.findall(r"[\u4e00-\u9fff]", text))
    english = len(re.findall(r"[a-zA-Z]+", text))
    return chinese + english


def scan_vault(vault_path: Path) -> dict:
    skip_dirs = {".obsidian", ".git", ".trash", "node_modules"}
    files = []
    attachments: dict[str, list[str]] = {}

    md_files = sorted(
        f for f in vault_path.rglob("*.md")
        if not any(part in skip_dirs for part in f.parts)
    )

    for md_file in md_files:
        rel = str(md_file.relative_to(vault_path))
        content = md_file.read_text(encoding="utf-8", errors="replace")
        post = frontmatter.loads(content)
        images = extract_images(content)

        created = extract_date_from_filename(md_file.name)
        if not created and "created" in post.metadata:
            created = str(post.metadata["created"])
        if not created:
            ts = md_file.stat().st_mtime
            created = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")

        preview = post.content[:200].replace("\n", " ").strip()

        files.append({
            "path": rel,
            "size_bytes": md_file.stat().st_size,
            "word_count": count_words(post.content),
            "created": created,
            "has_frontmatter": bool(post.metadata),
            "has_images": len(images) > 0,
            "images": images,
            "preview": preview,
        })

        for img in images:
            attachments.setdefault(img, []).append(rel)

    # Scan non-md attachments
    all_attachments = []
    for f in vault_path.rglob("*"):
        if f.is_file() and f.suffix.lower() != ".md" and not any(
            part in skip_dirs for part in f.parts
        ):
            rel = str(f.relative_to(vault_path))
            all_attachments.append({
                "path": rel,
                "size_bytes": f.stat().st_size,
                "extension": f.suffix.lower(),
                "referenced_by": attachments.get(f.name, []),
            })

    return {
        "scan_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "vault_path": str(vault_path),
        "total_md_files": len(files),
        "total_attachments": len(all_attachments),
        "files": files,
        "attachments": all_attachments,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run scan.py <vault_path> [output_path]")
        sys.exit(1)

    vault_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("manifest.json")

    if not vault_path.is_dir():
        print(f"Error: {vault_path} is not a valid directory")
        sys.exit(1)

    manifest = scan_vault(vault_path)
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"Scan complete: {manifest['total_md_files']} md files, {manifest['total_attachments']} attachments")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
