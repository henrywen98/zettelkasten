# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AutoPARA is a Claude Code plugin that uses AI to automatically organize Obsidian vaults. Based on the PARA methodology (Projects/Areas/Resources/Archives), it archives inbox materials, compiles a wiki knowledge layer, and generates visualizations.

## Development Commands

### Python Scripts (in `plugins/autopara/scripts/`)

```bash
# Install dependencies (requires uv, Python >=3.12)
cd plugins/autopara/scripts && uv sync

# Scan vault to generate manifest
uv run scan.py <vault_path> [output_path]

# Rewrite image/attachment links
uv run relink.py <md_file> <old_prefix> <new_prefix>

# Post-migration validation
uv run validate.py <vault_path> <manifest_path>
```

No test suite or lint configuration exists.

## Architecture

### Two-Layer Design: AI Workflows + Deterministic Scripts

**Skills (AI layer)** — SKILL.md files in `plugins/autopara/skills/` define AI-driven workflows:
- `para-ingest` — Daily workhorse: process inbox files → archive + update wiki
- `para-migrate` — One-time full vault migration, uses worktree + teammates for parallel execution
- `para-query` — Knowledge base Q&A
- `para-lint` — Health check (broken links, orphan pages, frontmatter completeness)
- `para-viz` — Generate Marp/Mermaid/Matplotlib visualizations
- `para-status` — Stats dashboard

**Scripts (deterministic layer)** — Python scripts in `plugins/autopara/scripts/` handle precise operations unsuitable for AI:
- `scan.py` — Walks vault, extracts metadata from every .md file, outputs manifest.json
- `relink.py` — Rewrites image paths after file moves (supports both `![](path)` and `![[path]]` Obsidian syntax)
- `validate.py` — Compares manifest against actual vault state, checks for missing/empty files, broken links, frontmatter completeness

Design principle: AI handles content analysis and generation; scripts handle file scanning and validation.

### Reference Specs (`plugins/autopara/references/`)

- `frontmatter-spec.md` — Archive files require 7 fields (title/created/archived/tags/summary/concepts/source); wiki files require 5 (title/type/sources/related/last_compiled)
- `vault-structure.md` — Target directory layout. Core principle: inbox belongs to the user, wiki belongs to AI, archive is the bridge

### Plugin Structure

```
auto-para/                                       # Marketplace root
├── .claude-plugin/marketplace.json              # Marketplace manifest
└── plugins/autopara/                            # Plugin root
    ├── .claude-plugin/plugin.json               # Plugin manifest
    ├── skills/<name>/SKILL.md                   # Workflow definitions per skill
    ├── scripts/                                 # Python deterministic scripts
    └── references/                              # Frontmatter and vault structure specs
```

Install: `/plugin marketplace add henrywen98/auto-para`, then `/plugin install autopara@auto-para`.

### para-migrate Parallel Execution Model

Migration is the most complex workflow, split into 4 phases:
1. **Scan** (scan.py) → manifest.json
2. **Plan** (AI reads previews in batches, generates migration-plan.json) → pauses for user review
3. **Execute** (~40 files per teammate, isolated via git worktrees, merged after completion)
4. **Validate** (validate.py) → validation-report.md

## Notes

- `manifest.json` and `.venv/` in scripts/ are gitignored — do not commit
- relink.py can be imported as a module (`from relink import relink_content`) or run standalone via CLI
- validate.py checks archive files for 7 required frontmatter fields and wiki files for 5
- scan.py word count is bilingual: Chinese counted per character, English per word
