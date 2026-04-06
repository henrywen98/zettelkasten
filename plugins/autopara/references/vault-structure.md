# Vault Target Structure

```
Vault/
├── 0_inbox/        — Single entry point, drop your materials here
├── 1_wiki/         — AI-compiled and maintained
│   ├── _index.md   — Master index
│   ├── _tags.md    — Tag index
│   ├── concepts/   — Concept articles
│   ├── topics/     — Topic aggregation pages
│   └── viz/        — Visualization outputs
├── 2_output/       — Query results
├── 3_archive/      — Archived originals (3_archive/YYYY-MM/)
└── 4_assets/       — Images & attachments
```

## Principles

- 0_inbox/ belongs to the user, 1_wiki/ belongs to AI, 3_archive/ is the bridge
- Classification is done via tags and wiki links, not folder hierarchy
- 4_assets/ manages all images/attachments centrally, md files reference via relative paths
