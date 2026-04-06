# AutoPARA

AI-powered Obsidian vault organizer — drop materials into inbox, let AI archive, compile wiki, and generate visualizations.

> A Claude Code plugin.

## Inspiration

- **[Andrej Karpathy](https://x.com/karpathy)**'s Obsidian workflow — the idea of using AI to actively organize and compile a knowledge base
- **[Tiago Forte](https://fortelabs.com/)**'s PARA method — the Projects / Areas / Resources / Archives organizational framework

AutoPARA combines both: PARA's structural principles to organize the vault, and AI to automate archiving, extraction, and compilation — solving the "good at capturing, bad at organizing" problem.

## Installation

```bash
# Add marketplace
/plugin marketplace add henrywen98/auto-para

# Install plugin
/plugin install autopara@auto-para
```

## Commands

| Command | Description |
|---------|-------------|
| `/para ingest <file>` | Process inbox files — archive to `3_archive/` and compile into `1_wiki/` |
| `/para query <question>` | Ask questions against your knowledge base, get structured answers |
| `/para lint` | Health check: broken links, orphan pages, tag inconsistencies, missing frontmatter |
| `/para viz <topic>` | Generate visualizations: Marp slides / Mermaid diagrams / Matplotlib charts |
| `/para status` | View knowledge base stats: file counts, tag distribution, inbox backlog |
| `/para migrate` | One-time full migration of an existing vault into AutoPARA structure |

## How It Works

```
Drop files into 0_inbox/
        |
   /para ingest
        |
        v
+-----------------------------------+
| 1. Analyze content                 |
| 2. Generate frontmatter            |
| 3. Archive to 3_archive/YYYY-MM/  |
| 4. Move images to 4_assets/       |
| 5. Compile into 1_wiki/           |
+-----------------------------------+
        |
        v
  1_wiki/ ready to browse
```

- **0_inbox/** — Single entry point, drop your materials here
- **3_archive/** — Original files archived by year-month, with AI-generated frontmatter
- **1_wiki/** — AI-compiled knowledge layer (concept articles, topic pages, tag index)
- **2_output/** — Query results
- **4_assets/** — Centralized image/attachment storage

## Vault Structure

```
Vault/
├── 0_inbox/        — Single entry point
├── 1_wiki/         — AI-compiled knowledge layer
│   ├── _index.md   — Master index
│   ├── _tags.md    — Tag index
│   ├── concepts/   — Concept articles
│   ├── topics/     — Topic aggregation pages
│   └── viz/        — Visualizations
├── 2_output/       — Query results
├── 3_archive/      — Archived originals (3_archive/YYYY-MM/)
└── 4_assets/       — Images & attachments
```

## Quick Start

1. Add marketplace: `/plugin marketplace add henrywen98/auto-para`
2. Install plugin: `/plugin install autopara@auto-para`
3. Initialize your vault: `/para migrate` (one-time migration to AutoPARA structure)
4. Daily use: drop materials into `0_inbox/`, run `/para ingest`

## Tech Stack

- **Claude Code Plugin** — SKILL.md-driven AI workflows
- **Python (uv)** — Deterministic file operations (scan, validate, link rewriting)
- **python-frontmatter** — YAML frontmatter parsing
- **Marp / Mermaid / Matplotlib** — Multi-format visualization output
- **Git + Git LFS** — Version control with LFS for binary files

## License

MIT
