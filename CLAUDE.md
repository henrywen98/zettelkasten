# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Zettelkasten is a Claude Code plugin that automatically organizes Obsidian vaults using the Zettelkasten methodology. Users drop files into 0_inbox/; AI atomizes content into permanent notes, builds wikilinks, and maintains MOC (Maps of Content) navigation.

## Architecture

### Pure Skill + Agent Plugin

No Python, no external dependencies. Three skills handle user commands; one agent handles batch processing:

- `zet-ingest` (skill) — Orchestrator: scans inbox, processes files directly or dispatches zet-worker agents for large batches
- `zet-query` (skill) — Knowledge base Q&A: navigates MOCs and notes to answer questions
- `zet-lint` (skill) — Health check: orphan notes, broken links, frontmatter completeness, MOC coverage
- `zet-worker` (agent) — Batch executor: processes ~10 inbox files per instance, dispatched by zet-ingest

Skills reference specs via `${CLAUDE_PLUGIN_ROOT}` — resolves to the plugin root at runtime.

### Vault = Current Working Directory

Claude Code is launched inside the Obsidian vault. All paths are relative — no vault_path parameter needed.

### Key Patterns

- **Atomic notes**: Each note in 1_zettel/ contains one concept. Multi-topic inbox files are split.
- **Connection forcing**: Every new note must link to ≥1 existing note via contextual wikilinks.
- **MOC auto-maintenance**: When a tag accumulates ≥3 notes, a MOC is created/updated in 2_maps/.
- **Inbox is ephemeral**: Processed files are deleted from 0_inbox/, not archived.
- **Batch threshold**: ≤10 inbox files processed directly; >10 dispatched to parallel zet-worker agents.

## Notes

- Install via Claude Code plugin marketplace: `github:henrywen98/zettelkasten`
- Frontmatter schema in `references/frontmatter-spec.md`
- Vault directory layout in `references/vault-structure.md`
