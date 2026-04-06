#!/usr/bin/env python3
"""Post-migration validation: compare manifest.json against actual vault state.

Usage: uv run validate.py <vault_path> <manifest_path>
Output: validation-report.md
"""

import json
import re
import sys
from pathlib import Path

import frontmatter

REQUIRED_ARCHIVE_FIELDS = {"title", "created", "archived", "tags", "summary", "concepts", "source"}
REQUIRED_WIKI_FIELDS = {"title", "type", "sources", "related", "last_compiled"}


def validate(vault_path: Path, manifest_path: Path) -> tuple[str, dict]:
    manifest = json.loads(manifest_path.read_text())
    original_count = manifest["total_md_files"]

    skip_dirs = {".obsidian", ".git", ".trash", "node_modules"}
    current_files = [
        f for f in vault_path.rglob("*.md")
        if not any(part in skip_dirs for part in f.parts)
    ]

    issues: list[str] = []
    warnings: list[str] = []
    stats = {
        "original_count": original_count,
        "current_count": len(current_files),
        "archive_count": 0,
        "wiki_count": 0,
        "inbox_count": 0,
        "empty_files": 0,
        "missing_frontmatter": 0,
        "broken_links": 0,
    }

    for f in current_files:
        rel = str(f.relative_to(vault_path))
        content = f.read_text(encoding="utf-8", errors="replace")

        if len(content.strip()) == 0:
            issues.append(f"Empty file: {rel}")
            stats["empty_files"] += 1
            continue

        if rel.startswith("3_archive/"):
            stats["archive_count"] += 1
            post = frontmatter.loads(content)
            missing = REQUIRED_ARCHIVE_FIELDS - set(post.metadata.keys())
            if missing:
                issues.append(f"Archive frontmatter missing fields {missing}: {rel}")
                stats["missing_frontmatter"] += 1

        elif rel.startswith("1_wiki/") and not rel.startswith("1_wiki/_"):
            stats["wiki_count"] += 1
            post = frontmatter.loads(content)
            missing = REQUIRED_WIKI_FIELDS - set(post.metadata.keys())
            if missing:
                issues.append(f"Wiki frontmatter missing fields {missing}: {rel}")
                stats["missing_frontmatter"] += 1

        elif rel.startswith("0_inbox/"):
            stats["inbox_count"] += 1

        for img in re.findall(r"!\[.*?\]\((.+?)\)", content):
            if img.startswith("http"):
                continue
            img_path = (f.parent / img).resolve()
            if not img_path.exists():
                issues.append(f"Broken link: {rel} -> {img}")
                stats["broken_links"] += 1

        for img in re.findall(r"!\[\[(.+?)\]\]", content):
            candidates = list(vault_path.rglob(Path(img).name))
            if not candidates:
                issues.append(f"Broken link: {rel} -> ![[{img}]]")
                stats["broken_links"] += 1

    if stats["current_count"] < original_count:
        diff = original_count - stats["current_count"]
        issues.append(f"File count decreased: original {original_count}, current {stats['current_count']} (diff {diff})")

    report = f"""# Migration Validation Report

## Statistics

| Metric | Value |
|--------|-------|
| Original file count | {stats['original_count']} |
| Current file count | {stats['current_count']} |
| 3_archive/ | {stats['archive_count']} |
| 1_wiki/ | {stats['wiki_count']} |
| 0_inbox/ | {stats['inbox_count']} |
| Empty files | {stats['empty_files']} |
| Missing frontmatter | {stats['missing_frontmatter']} |
| Broken links | {stats['broken_links']} |

## Issues ({len(issues)} items)

"""
    if issues:
        for issue in issues:
            report += f"- {issue}\n"
    else:
        report += "No issues found.\n"

    if warnings:
        report += f"\n## Warnings ({len(warnings)} items)\n\n"
        for w in warnings:
            report += f"- {w}\n"

    return report, stats


def main():
    if len(sys.argv) < 3:
        print("Usage: uv run validate.py <vault_path> <manifest_path>")
        sys.exit(1)

    vault_path = Path(sys.argv[1])
    manifest_path = Path(sys.argv[2])
    report, stats = validate(vault_path, manifest_path)

    output = vault_path / "validation-report.md"
    output.write_text(report, encoding="utf-8")
    print(f"Validation report generated: {output}")

    if stats["current_count"] < stats["original_count"] or stats["empty_files"] > 0:
        print("Warning: issues found, please review the report")
        sys.exit(1)
    else:
        print("Validation passed")


if __name__ == "__main__":
    main()
