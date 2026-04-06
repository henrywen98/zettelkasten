# Zettelkasten

AI-powered Obsidian vault organizer — drop materials into inbox, AI atomizes into permanent notes, builds links, and maintains MOC navigation.

> A Claude Code plugin using the Zettelkasten methodology.

## How It Works

1. Drop files into `0_inbox/` — notes, web clips, imports, anything
2. Run `/zet ingest` — AI reads, atomizes, rewrites, links, and organizes
3. Browse `1_zettel/` for your permanent notes, `2_maps/` for topic navigation
4. Run `/zet query <question>` to search and synthesize from your knowledge base
5. Run `/zet lint` to check vault health

## Vault Structure

```
Vault/
├── 0_inbox/     — Drop materials here
├── 1_zettel/    — Permanent notes (atomic, linked, by year-month)
├── 2_maps/      — MOC navigation (AI maintained)
├── 3_output/    — Query results, lint reports
└── 4_assets/    — Images and attachments
```

## Commands

| Command | Description |
|---------|-------------|
| `/zet ingest [target]` | Process inbox files into Zettelkasten notes |
| `/zet query <question>` | Ask questions against your knowledge base |
| `/zet lint` | Health check: orphans, broken links, frontmatter |

## Installation

```bash
/plugins install github:henrywen98/zettelkasten
```

## Requirements

- Claude Code
- An Obsidian vault (or any markdown folder)
- Git initialized in the vault (for backup safety)

## License

MIT
