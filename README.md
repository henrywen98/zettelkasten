# Zettelkasten — AI-Powered Note Organizer for Obsidian

[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-Plugin-blue)](https://docs.anthropic.com/en/docs/claude-code)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Automatically organize your Obsidian vault using the Zettelkasten method.** Drop files into inbox, AI atomizes content into permanent atomic notes, builds wikilinks, and maintains Maps of Content (MOC) — powered by Claude Code.

> Zero dependencies. No Python, no scripts — pure Claude Code skills + agents.

[中文版](README_CN.md)

## The Problem

You clip articles, jot ideas, save snippets — and they pile up in a folder, **unlinked and forgotten**. Manual note organization doesn't scale. Your second brain stays dumb.

## The Solution

This plugin turns your Obsidian vault into a self-organizing knowledge base:

- **Atomize** — One concept per note. Multi-topic files are automatically split.
- **Rewrite** — Clean prose with proper structure, preserving all original information.
- **Link** — Every note connects to existing knowledge via contextual wikilinks. Cross-domain connections preferred.
- **Navigate** — Maps of Content (MOC) auto-generated when topics accumulate ≥3 notes.

## Quick Start

### 1. Install the Plugin

```bash
# In Claude Code
/plugins install github:henrywen98/zettelkasten
```

### 2. Set Up Your Vault

```bash
cd /path/to/your/obsidian/vault
mkdir -p 0_inbox 1_zettel 2_maps 3_output 4_assets
git init  # recommended for version safety
```

### 3. Ingest Your First Notes

Drop any files (notes, web clips, article exports) into `0_inbox/`, then:

```bash
cd /path/to/your/vault
claude
```

```
> /zet-ingest
```

That's it. Atomic notes appear in `1_zettel/`, organized by year-month, interlinked, with MOC navigation in `2_maps/`.

## Features

### `/zet-ingest` — Inbox to Knowledge Base

The core workflow. Scans `0_inbox/`, dispatches AI agents to process files in batches of ~10, then updates MOCs and commits via git.

Each file goes through: **read → classify → atomize → rewrite → frontmatter → link → write**.

```
0_inbox/weekly-learning.md          →  1_zettel/2026-04/ssh-key-authentication.md
  (SSH + Python decorators + Docker)    1_zettel/2026-04/python-decorator-patterns.md
                                        1_zettel/2026-04/docker-compose-networking.md
```

- Multi-topic files split into independent atomic notes
- Each note links to ≥1 existing note (connection forcing)
- Original language preserved (Chinese stays Chinese, English stays English)
- Source files deleted after processing — inbox stays clean

### `/zet-query` — Ask Your Knowledge Base

Query your accumulated knowledge in natural language. The AI navigates MOCs and note links, reads relevant notes, and synthesizes an answer with `[[wikilink]]` citations.

```
> /zet-query What do I know about authentication?
```

Output saved to `3_output/` with full source references.

### `/zet-lint` — Vault Health Check

Structural integrity scanner:

- Broken wikilinks pointing to non-existent notes
- Orphan notes with no inbound or outbound links
- Incomplete frontmatter (missing required fields)
- MOC coverage gaps — uncategorized notes
- Stale MOC counts

Auto-fix offered for common issues.

## Vault Structure

```
Vault/
├── 0_inbox/        Drop materials here (deleted after processing)
├── 1_zettel/       Permanent notes — atomic, linked, by year-month
│   └── YYYY-MM/    e.g. 2026-04/
├── 2_maps/         Maps of Content — auto-maintained topic navigation
├── 3_output/       Query results, lint reports
└── 4_assets/       Images and attachments
```

## Note Format

Every permanent note follows a consistent structure with YAML frontmatter:

```yaml
---
id: "202604061430"
title: "SSH Key Authentication"
created: 2026-04-06
processed: 2026-04-06
source: web-clip          # original | web-clip | import
tags: [ssh, security, devops]
summary: "How SSH key-based authentication works — key generation, exchange, and verification flow"
---

# SSH Key Authentication

[Note content in clear prose...]

## Links
- Related to [[tls-handshake-protocol]]: both use asymmetric cryptography for initial authentication
- See [[server-hardening-checklist]]: SSH key auth is a key step in hardening
```

## How It Works

```
/zet-ingest
    │
    ▼
zet-ingest (skill)          ← Orchestrator: scan, batch, dispatch, MOC, commit
    │
    ├── zet-worker (agent)  ← Batch 1: read → atomize → rewrite → link → write
    ├── zet-worker (agent)  ← Batch 2: can link to batch 1's notes
    └── ...                 ← Sequential processing, each batch commits before next
```

| Component | Role |
|-----------|------|
| **zet-ingest** | Orchestrator — scans inbox, batches files, dispatches workers, updates MOCs, git commits |
| **zet-worker** | File processor — reads, atomizes, rewrites, links, writes. ~10 files per batch |
| **zet-query** | Knowledge Q&A — navigates MOCs + full-text search to answer questions |
| **zet-lint** | Health checker — finds structural issues, offers auto-fix |

Batches run sequentially — each commits before the next starts. Later batches discover and link to earlier notes, improving link quality progressively. You can interrupt between batches without losing work.

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (CLI, desktop app, or IDE extension)
- An Obsidian vault (or any markdown folder)
- Git initialized in the vault (recommended)

## Model Recommendations

| Model | Best for |
|-------|----------|
| **Sonnet** | Daily ingestion — fast, reliable, good link quality |
| **Opus** | High-value content — best atomization judgment and cross-domain linking |

## Related Concepts

- [Zettelkasten Method](https://zettelkasten.de/introduction/) — The note-taking methodology behind this plugin
- [Atomic Notes](https://notes.andymatuschak.org/Evergreen_notes_should_be_atomic) — Andy Matuschak on why one concept per note matters
- [Maps of Content](https://www.linkingyourthinking.com/) — Nick Milo's MOC concept for navigating linked notes
- [Building a Second Brain](https://www.buildingasecondbrain.com/) — Tiago Forte's PARA method for organizing digital knowledge

## Inspiration

Inspired by [Andrej Karpathy](https://karpathy.ai/)'s ideas on building a personal knowledge base with AI — letting machines handle the organizing so you can focus on thinking.

## Contact

Questions, suggestions, or feedback? Reach out at **henrywen98@gmail.com**

## License

MIT
