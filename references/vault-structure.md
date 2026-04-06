# Vault Structure

```
Vault/  (= current working directory)
├── 0_inbox/        — User drops materials here (ephemeral, deleted after processing)
├── 1_zettel/       — Permanent notes, atomic, linked (by year-month subdirectory)
│   └── YYYY-MM/    — e.g. 2026-04/
├── 2_maps/         — MOC structure notes (AI maintained, user editable)
├── 3_output/       — Query results, lint reports
└── 4_assets/       — Images and attachments
```

## Ownership Rules

| Directory | Owner | AI Access |
|-----------|-------|-----------|
| 0_inbox/ | User | Read + delete after processing |
| 1_zettel/ | AI generates, user may edit | Full |
| 2_maps/ | AI maintains, user may edit | Full |
| 3_output/ | AI generates | Write |
| 4_assets/ | AI organizes | Move files in |

## Principles

- No vault_path parameter — Claude Code is launched inside the vault, all paths are relative
- Year-month subdirectories in 1_zettel/ prevent flat-folder explosion
- Wikilinks [[]] throughout — Obsidian native, path-independent
- Inbox is ephemeral — processed files are deleted, not archived
- Classification via tags and wikilinks, not folder hierarchy
- 4_assets/ manages all images/attachments centrally

## Image Handling

- All images referenced by inbox files move to 4_assets/
- Update references to wikilink format: ![[image.png]]
- If image already exists in 4_assets/, skip move
- Support both ![](path) and ![[path]] input formats

## MOC Rules

- When a tag accumulates ≥3 notes across 1_zettel/, create or update a MOC in 2_maps/
- Each MOC entry includes a one-line description
- MOCs can link to other MOCs (related maps section)
