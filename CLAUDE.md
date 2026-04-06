# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Zettelkasten is a Claude Code plugin that automatically organizes Obsidian vaults using the Zettelkasten methodology. Users drop files into 0_inbox/; AI atomizes content into permanent notes, builds wikilinks, and maintains MOC (Maps of Content) navigation.

## Architecture

### Pure Skill + Agent Plugin

No Python, no external dependencies. Three skills handle user commands; one agent handles batch processing:

- `zet-ingest` (skill) — Pure orchestrator: scans inbox, batches files, dispatches zet-worker, updates MOCs, commits
- `zet-query` (skill) — Knowledge base Q&A: navigates MOCs and notes to answer questions
- `zet-lint` (skill) — Health check: 10 checks (orphans, broken links, frontmatter, MOC coverage, tag consistency, image refs, duplicates) + auto-fix
- `zet-worker` (agent) — Sole file processor: ~10 files per batch, 8-step pipeline (read → atomize → rewrite → frontmatter → links → dedup → write → images)

Skills reference specs via `${CLAUDE_PLUGIN_ROOT}` — resolves to the plugin root at runtime.

### Vault = Current Working Directory

Claude Code is launched inside the Obsidian vault. All paths are relative — no vault_path parameter needed.

### Key Patterns

- **Atomic notes**: Each note in 1_zettel/ contains one concept. Multi-topic inbox files are split.
- **Connection forcing**: Every new note must link to ≥1 existing note via contextual wikilinks.
- **MOC auto-maintenance**: When a tag accumulates ≥3 notes, a MOC is created/updated in 2_maps/.
- **Inbox is ephemeral**: Processed files are deleted from 0_inbox/, not archived.
- **Sequential batching**: All files dispatched to zet-worker in batches of ~10, processed one batch at a time, each batch commits before next begins.
- **Atomization rules**: Split decisions follow three tests (title/tag/independence) defined in `references/atomization-rules.md`.
- **Tag normalization**: All tags lowercase kebab-case (`AI` → `ai`). Defined in `references/frontmatter-spec.md`.
- **Dedup on ingest**: Worker checks for existing notes with same title before writing, skips exact duplicates.

## Plugin Structure

This repo serves dual role: it is both a **marketplace** (registered in `known_marketplaces.json`) and the **plugin** itself (`source: "./"` in `marketplace.json`).

```
.claude-plugin/
  plugin.json          # Only name/version/description (henry-hub convention)
  marketplace.json     # Marketplace manifest
skills/<name>/SKILL.md # Skill definitions
agents/<name>.md       # Agent definitions
references/            # Shared specs referenced via ${CLAUDE_PLUGIN_ROOT}
```

### Skill Frontmatter

Standard fields only: `name` and `description`. Do not use `user-invocable`, `arguments`, or other non-standard fields — they may cause parsing issues and prevent skills from appearing in `/` autocomplete.

## Development Workflow

```bash
# 1. Edit in dev repo
cd /Users/henry/dev/2_areas/zettelkasten

# 2. Commit & push
git add . && git commit -m "fix: ..." && git push

# 3. Sync installed copy
cd /Users/henry/.claude/plugins/marketplaces/zettelkasten && git pull

# 4. Test: open a new Claude Code session in the Obsidian vault
cd /Users/henry/Documents/6_ob && claude
# Type /zet-ingest, /zet-query, /zet-lint to verify
```

Never edit the installed copy directly — changes will be overwritten on next `git pull`.

## Conventions

- All code, comments, documentation, and commit messages in this repository use **English**.

## Notes

- Install via Claude Code plugin marketplace: `github:henrywen98/zettelkasten`
- Frontmatter schema in `references/frontmatter-spec.md`
- Vault directory layout in `references/vault-structure.md`
- Atomization rules in `references/atomization-rules.md`
- MOC management rules in `references/moc-rules.md`
