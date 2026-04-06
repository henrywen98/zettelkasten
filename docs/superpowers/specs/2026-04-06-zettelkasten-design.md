# Zettelkasten — AI-Powered Obsidian Knowledge Base Plugin

## Overview

A Claude Code plugin that automatically organizes an Obsidian vault using Zettelkasten methodology. Users drop materials into inbox; AI atomizes content into permanent notes, builds links, and maintains MOC navigation — fully automated. The thinking happens at query time, not at ingestion time.

**Plugin name**: `zettelkasten`
**Command prefix**: `/zet`
**Repository**: `henrywen98/zettelkasten`
**Dependencies**: None (pure Claude Code skills + agent, zero Python)

---

## 1. Vault Structure

```
Vault/  (= current working directory, Claude Code launched here)
├── 0_inbox/           # User drops materials here (fleeting notes, deleted after processing)
├── 1_zettel/          # Permanent notes — atomic, linked, by year-month
│   ├── 2026-04/
│   └── .../
├── 2_maps/            # MOC structure notes — AI maintained, user editable
│   └── <topic>.md
├── 3_output/          # Query results, lint reports
└── 4_assets/          # Images and attachments
```

### Ownership Rules

| Directory | Owner | AI Access |
|-----------|-------|-----------|
| `0_inbox/` | User | Read + delete after processing |
| `1_zettel/` | AI generates, user may edit | Full |
| `2_maps/` | AI maintains, user may edit | Full |
| `3_output/` | AI generates | Write |
| `4_assets/` | AI organizes | Move files in |

### Design Decisions

- **No vault_path parameter** — Claude Code is launched inside the vault, all paths are relative
- **Year-month subdirectories** in `1_zettel/` — prevents flat-folder explosion with thousands of notes
- **Wikilinks `[[]]`** throughout — Obsidian native, path-independent, graph-view compatible
- **Inbox is ephemeral** — processed files are deleted, not archived. No archive layer.

---

## 2. Frontmatter Spec

### Permanent Notes (`1_zettel/`)

```yaml
---
id: "202604061430"           # Timestamp ID, unique identifier
title: "SSH 密钥认证原理"     # Atomic title — one concept
created: 2026-04-06          # Original material creation date
processed: 2026-04-06        # Date AI processed this note
source: original             # original | web-clip | import
tags: [ssh, devops, 安全]
summary: "SSH 使用非对称加密实现免密登录"
---

Note body...

## Links
- Related to [[非对称加密基础]]: SSH key auth is a typical application
- See [[远程服务器管理]]: key config is a prerequisite for remote management
```

**Required frontmatter fields (7)**: `id`, `title`, `created`, `processed`, `source`, `tags`, `summary`.
**Required body structure**: A `## Links` section at the end with contextual wikilinks to related notes.

### MOC Structure Notes (`2_maps/`)

```yaml
---
title: "DevOps"
type: map                    # map | hub
note_count: 12               # Auto-updated by AI
last_updated: 2026-04-06
---

# DevOps

## Core Concepts
- [[SSH 密钥认证原理]] — foundation for passwordless login
- [[Docker 容器网络]] — container communication mechanisms

## Related Maps
- [[Linux 系统管理]]
- [[CI/CD 流水线]]
```

**Required fields (4)**: `title`, `type`, `note_count`, `last_updated`.

### Query Output (`3_output/`)

```yaml
---
title: "���于 SSH 的查询"
query: "SSH 密钥怎么配置？"
date: 2026-04-06
sources: ["1_zettel/2026-04/ssh-key-authentication.md"]
---
```

**Required fields (4)**: `title`, `query`, `date`, `sources`.

---

## 3. Plugin Structure

```
zettelkasten/                          # Repo root = plugin root
├── .claude-plugin/
│   └── plugin.json                    # name: zettelkasten
├── skills/
│   ├── zet-ingest/
│   │   └── SKILL.md                   # Orchestrator: scan inbox, dispatch or process
│   ├── zet-query/
│   │   └── SKILL.md                   # Knowledge base Q&A
│   └── zet-lint/
│       └── SKILL.md                   # Health check
├── agents/
│   └── zet-worker.md                  # Batch processing executor
├── references/
│   ├── frontmatter-spec.md            # Frontmatter schema
│   └── vault-structure.md             # Vault directory spec
├── CLAUDE.md
└── README.md
```

All operations use Claude Code built-in tools:
- File I/O: Read, Write, Edit, Glob, Grep
- File moves: Bash (`mv`)
- Git: Bash (`git add`, `git commit`)

---

## 4. Component Design

### 4.1 zet-ingest (skill)

**Trigger**: `/zet ingest [target]`
**Role**: Orchestrator — scans inbox, decides direct processing vs batch dispatch.

**Flow**:

```
/zet ingest [target]
    │
    ├─ Scan 0_inbox/ (or target glob)
    ├─ Count files
    │
    ├─ ≤10 files: process directly in current conversation
    │   ├─ For each file:
    │   │   ├─ Read full content
    │   │   ├─ Determine source type (original / web-clip / import)
    │   │   ├─ Atomize: split into independent concepts if multi-topic
    │   ��   ├─ Rewrite in clear prose (preserve core info, improve structure)
    │   │   ├─ Generate frontmatter (id, title, tags, summary, etc.)
    │   │   ├─ Build links: Grep 1_zettel/ for related notes, add contextual [[]] links
    │   │   ├─ Write to 1_zettel/YYYY-MM/<slug>.md
    │   │   ├─ Move images to 4_assets/, update references to ![[image.png]]
    │   │   └─ Delete source file from 0_inbox/
    │   ├─ Update relevant MOCs in 2_maps/
    │   └─ git commit
    │
    └─ >10 files: batch dispatch
        ├─ Split into batches of ~10 files
        ├��� Dispatch zet-worker agent per batch (shared working directory)
        ├─ Workers: process files, skip MOC updates
        ├─ Wait for all workers to complete
        ├─ Consolidate: update MOCs in 2_maps/
        ├─ Delete processed source files from 0_inbox/
        └─ git commit
```

**Atomization rules** (encoded in skill and agent):
- One note = one independent concept/idea
- Multi-topic with unrelated sections → split into separate notes
- Coherent single-topic with multiple aspects → keep as one note
- Each split note must be self-contained (understandable without the original)
- If source has only one topic, do not split

**Link building rules**:
- Every new note must link to ≥1 existing note (connection forcing)
- Links must have context explanation (not bare `[[]]`)
- Prioritize cross-domain "surprise" connections over obvious same-topic links
- Use Grep to search `1_zettel/` for semantic matches

**MOC maintenance rules**:
- When a tag accumulates ≥3 notes, create or update a MOC in `2_maps/`
- Each MOC entry includes a one-line description
- MOCs can link to other MOCs (related maps)

### 4.2 zet-worker (agent)

**Role**: Batch executor, dispatched by zet-ingest for large inbox processing.
**Model**: inherit
**Color**: green
**Tools**: Read, Write, Edit, Glob, Grep, Bash

**Responsibilities**:
1. Receive a batch of file paths
2. For each file: read → atomize → rewrite → frontmatter → build links → write to 1_zettel/ → move images
3. Skip MOC updates (orchestrator handles this after all workers finish)
4. Report results: files processed, notes generated, links created

**Does NOT**:
- Update MOCs (avoids write conflicts between workers)
- Git commit (orchestrator does a single commit)
- Delete inbox files (orchestrator handles cleanup)

### 4.3 zet-query (skill)

**Trigger**: `/zet query <question>`
**Role**: Knowledge base Q&A — the "thinking stage" where the user engages with their knowledge.

**Flow**:
1. Read MOCs in `2_maps/` to locate relevant topics
2. Follow MOC links + Grep `1_zettel/` for keyword matches
3. Read relevant permanent notes
4. Synthesize a structured answer
5. Save to `3_output/YYYY-MM-DD-<slug>.md` with frontmatter

### 4.4 zet-lint (skill)

**Trigger**: `/zet lint`
**Role**: Health check — detect structural problems in the knowledge base.

**Checks**:
1. **Orphan notes** — `1_zettel/` notes with zero inbound or outbound links
2. **Missing links** — notes that have outbound but no inbound links, or vice versa
3. **Frontmatter completeness** — missing required fields per spec
4. **MOC coverage** — notes not referenced by any MOC
5. **Broken links** — wikilinks pointing to non-existent notes
6. **Empty files** — files with no content

**Output**: `3_output/lint-report-YYYY-MM-DD.md` with errors/warnings/suggestions.
**Auto-fix option**: offer to fix MOC gaps, create missing MOCs, update frontmatter.

---

## 5. Content Processing Rules

### Source Type Detection

| Type | Signals |
|------|---------|
| `original` | User-authored content, personal notes, reflections |
| `web-clip` | URLs, "Source:" headers, clipped formatting, blockquotes from articles |
| `import` | Structured data, exported from other tools, has existing frontmatter |

### Rewriting Principles

- **Preserve all core information** — nothing lost in rewriting
- **Improve structure** — add headings, clean formatting, fix markdown
- **Write in clear prose** — complete sentences, self-contained
- **Maintain language** — if original is Chinese, output Chinese; if English, output English
- **No copy-paste** — reformulate, don't just move text around

### Image Handling

- All images referenced by inbox files → move to `4_assets/`
- Update references to wikilink format: `![[image.png]]`
- If image already exists in `4_assets/`, skip move
- Support both `![](path)` and `![[path]]` input formats

---

## 6. Migration Strategy

No dedicated migration skill. Users handle migration incrementally:

1. User manually moves files into `0_inbox/` (in batches they're comfortable with)
2. Run `/zet ingest` — skill auto-detects count, processes directly or dispatches agents
3. Repeat until vault is fully migrated

This avoids the complexity of scan → plan → execute → validate pipeline from the previous design.

---

## 7. Constraints

- **No Python, no external dependencies** — pure Claude Code plugin
- **No vault_path parameter** — vault = current working directory
- **No real-time sync** — all operations are on-demand via `/zet` commands
- **No RAG/vector DB** — relies on Grep + MOC navigation for retrieval
- **AI never modifies user's inbox directly** — only reads and deletes after processing
- **Git backup assumed** — destructive operations (inbox deletion) assume user has git history
