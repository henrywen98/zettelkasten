# Zettelkasten Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude Code plugin that auto-organizes an Obsidian vault using Zettelkasten methodology — atomize inbox content into permanent notes, build links, maintain MOC navigation.

**Architecture:** Plugin with 3 skills (zet-ingest / zet-query / zet-lint) + 1 agent (zet-worker). Skills handle user-facing commands; agent handles batch file processing. Zero Python dependencies — all operations via Claude Code built-in tools.

**Tech Stack:** Claude Code plugin (SKILL.md, AGENT.md), Markdown, YAML frontmatter, Obsidian wikilinks

**Plugin-dev reference skills:** Each task below notes which `plugin-dev:*` skill to invoke for guidance on file format and best practices.

---

## File Structure

```
zettelkasten/                          # Repo root = plugin root
├── .claude-plugin/
│   └── plugin.json                    # Plugin manifest
├── skills/
│   ├── zet-ingest/
│   │   └── SKILL.md                   # Inbox processing orchestrator
│   ├── zet-query/
│   │   └── SKILL.md                   # Knowledge base Q&A
│   └── zet-lint/
│       └── SKILL.md                   # Health check
├── agents/
│   └── zet-worker.md                  # Batch processing executor
├── references/
│   ├── frontmatter-spec.md            # Frontmatter schema for all note types
│   └── vault-structure.md             # Vault directory layout and ownership rules
├── .gitignore
├── CLAUDE.md
└── README.md
```

**Files to delete** (old auto-para):
- `plugins/` (entire directory)
- `scripts/` (if exists at root)
- `autopara-architecture.drawio`

---

### Task 1: Clean Up Old Files + Scaffold Plugin

Remove all auto-para artifacts and create the new plugin skeleton.

**Invoke:** `plugin-dev:plugin-structure` for plugin.json format and directory conventions.

**Files:**
- Delete: `plugins/autopara/` (entire directory tree)
- Delete: `autopara-architecture.drawio`
- Create: `.claude-plugin/plugin.json`
- Modify: `.gitignore`

- [ ] **Step 1: Delete old plugin directory**

```bash
rm -rf plugins/
rm -f autopara-architecture.drawio
```

- [ ] **Step 2: Create plugin.json**

Write `.claude-plugin/plugin.json`:

```json
{
  "name": "zettelkasten",
  "version": "0.1.0",
  "description": "AI-powered Obsidian vault organizer — atomize inbox into Zettelkasten notes, build links, maintain MOC navigation"
}
```

- [ ] **Step 3: Create directory skeleton**

```bash
mkdir -p skills/zet-ingest skills/zet-query skills/zet-lint agents references
```

- [ ] **Step 4: Clean up .gitignore**

Replace entire `.gitignore` with:

```
.DS_Store
.claude/settings.local.json
```

Old Python-related entries (`__pycache__/`, `*.pyc`, `.venv/`, `*.egg-info/`, `dist/`, `uv.lock`, `manifest.json`, `validation-report.md`) are no longer needed.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore: remove auto-para, scaffold zettelkasten plugin structure"
```

---

### Task 2: Create Reference Specs

Shared reference documents that skills and agent read at runtime.

**Files:**
- Create: `references/frontmatter-spec.md`
- Create: `references/vault-structure.md`

- [ ] **Step 1: Write frontmatter-spec.md**

Write `references/frontmatter-spec.md`:

```markdown
# Frontmatter Spec

## Permanent Notes (1_zettel/)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Timestamp ID in YYYYMMDDHHmm format, unique identifier |
| title | string | yes | Atomic title — one concept per note |
| created | date (YYYY-MM-DD) | yes | Original material creation date |
| processed | date (YYYY-MM-DD) | yes | Date AI processed this note |
| source | enum: original, web-clip, import | yes | Source type |
| tags | string[] | yes | Tag list |
| summary | string | yes | One-line summary of the note's core idea |

### Source Type Detection

| Type | Signals |
|------|---------|
| original | User-authored content, personal notes, reflections |
| web-clip | URLs, "Source:" headers, clipped formatting, blockquotes from articles |
| import | Structured data, exported from other tools, has existing frontmatter |

### Required Body Structure

Every permanent note must end with a `## Links` section containing contextual wikilinks:

```
## Links
- Related to [[note-title]]: explanation of why these are connected
- See [[other-note]]: explanation of the relationship
```

Rules:
- Every note must link to ≥1 existing note (connection forcing)
- Links must include context — never bare `[[]]` without explanation
- Prefer cross-domain "surprise" connections over obvious same-topic links

## MOC Structure Notes (2_maps/)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | yes | Topic name |
| type | enum: map, hub | yes | map = topic-level, hub = domain-level |
| note_count | integer | yes | Number of linked notes (auto-updated) |
| last_updated | date (YYYY-MM-DD) | yes | Last update date |

## Query Output (3_output/)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | yes | Brief question summary |
| query | string | yes | Original query text |
| date | date (YYYY-MM-DD) | yes | Query date |
| sources | string[] | yes | Referenced file path list |
```

- [ ] **Step 2: Write vault-structure.md**

Write `references/vault-structure.md`:

```markdown
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
```

- [ ] **Step 3: Commit**

```bash
git add references/
git commit -m "feat: add frontmatter spec and vault structure references"
```

---

### Task 3: Create zet-worker Agent

The batch processing executor, dispatched by zet-ingest for large inbox volumes.

**Invoke:** `plugin-dev:agent-development` for AGENT.md frontmatter format, description with examples, and system prompt design.

**Files:**
- Create: `agents/zet-worker.md`

- [ ] **Step 1: Write zet-worker.md**

Write `agents/zet-worker.md`:

```markdown
---
name: zet-worker
description: >-
  Use this agent when processing a batch of inbox files into Zettelkasten permanent notes.
  This agent is dispatched by the zet-ingest skill when inbox has >10 files.
  It should NOT be invoked directly by users.

  <example>
  Context: The zet-ingest skill detected 35 files in 0_inbox/ and is splitting into batches.
  user: "/zet ingest"
  assistant: "Inbox has 35 files. Dispatching 4 zet-worker agents to process in parallel."
  <commentary>
  Large inbox volume triggers batch mode. Each worker processes ~10 files independently.
  </commentary>
  </example>

  <example>
  Context: The zet-ingest skill is processing a user-specified glob that matches 15 files.
  user: "/zet ingest 0_inbox/2026-04-*.md"
  assistant: "Found 15 matching files. Dispatching 2 zet-worker agents."
  <commentary>
  Targeted ingest with >10 matches still triggers batch dispatch.
  </commentary>
  </example>

model: inherit
color: green
tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
---

You are a Zettelkasten processing worker. You receive a batch of inbox file paths and transform each into atomic permanent notes.

**Reference specs (read these before processing):**
- Frontmatter: ${CLAUDE_PLUGIN_ROOT}/references/frontmatter-spec.md
- Vault structure: ${CLAUDE_PLUGIN_ROOT}/references/vault-structure.md

**Your Core Responsibilities:**

1. Process each assigned file from 0_inbox/
2. Atomize content into independent permanent notes
3. Write notes with proper frontmatter to 1_zettel/YYYY-MM/
4. Build contextual links to existing notes
5. Move images to 4_assets/ and update references

**Processing Each File:**

For each file in your batch:

1. **Read** the full content of the inbox file
2. **Detect source type**: original (user-written), web-clip (clipped from web), import (from other tools)
3. **Determine created date**: extract from filename (e.g. 20260114 pattern) > existing frontmatter > file modification time
4. **Atomize**: Identify independent concepts in the content
   - Multiple unrelated topics with separate sections → split into separate notes
   - One coherent topic with multiple aspects → keep as one note
   - Each resulting note must be understandable without the original
5. **Rewrite** each note in clear prose:
   - Preserve ALL core information — nothing lost
   - Improve structure, add headings, clean formatting
   - Maintain original language (Chinese → Chinese, English → English)
   - Reformulate, do not just copy-paste
6. **Generate frontmatter** per spec:
   - id: YYYYMMDDHHmm timestamp (use current time, increment minutes for splits from same source)
   - title: atomic title, one concept
   - created: from step 3
   - processed: today's date
   - source: from step 2
   - tags: relevant tags
   - summary: one-line summary
7. **Build links**: Search 1_zettel/ with Grep for semantically related notes
   - Add a `## Links` section with contextual wikilinks
   - Every note must link to ≥1 existing note
   - Format: `- Related to [[note-title]]: explanation`
   - Prefer cross-domain connections over obvious same-topic links
   - If 1_zettel/ is empty (first batch), link between notes in the current batch
8. **Write** the note to 1_zettel/YYYY-MM/<slug>.md (create directory if needed)
9. **Handle images**: If the file references images, move them to 4_assets/ and update references to `![[filename.png]]` wikilink format

**You Do NOT:**
- Update MOCs in 2_maps/ (the orchestrator handles this after all workers finish)
- Run git commit (the orchestrator commits once after all workers complete)
- Delete source files from 0_inbox/ (the orchestrator handles cleanup)

**Output:**
When finished, report:
- Number of inbox files processed
- Number of permanent notes created (may exceed files if atomization split content)
- Number of links created
- List of new note paths created
```

- [ ] **Step 2: Commit**

```bash
git add agents/
git commit -m "feat: add zet-worker agent for batch inbox processing"
```

---

### Task 4: Create zet-ingest Skill

The core daily-use skill — orchestrates inbox processing.

**Invoke:** `plugin-dev:skill-development` for SKILL.md format, third-person description, imperative body style.

**Files:**
- Create: `skills/zet-ingest/SKILL.md`

- [ ] **Step 1: Write zet-ingest SKILL.md**

Write `skills/zet-ingest/SKILL.md`:

```markdown
---
name: zet-ingest
description: >-
  This skill should be used when the user asks to "process inbox", "ingest notes",
  "organize inbox", "zet ingest", "digest notes", "process new notes",
  "archive inbox files", "handle new materials", or has new files in 0_inbox/ to process.
  Orchestrates Zettelkasten ingestion: atomizes inbox content into permanent notes,
  builds wikilinks, and maintains MOC navigation. The most frequently used daily command.
user-invocable: true
arguments:
  - name: target
    description: "File path or glob pattern, e.g. 0_inbox/*.md or a specific filename. Omit to process all .md files in 0_inbox/"
    required: false
---

# Zettelkasten Ingest — Process Inbox

Atomize inbox content into permanent notes in 1_zettel/, build links, and update MOC navigation in 2_maps/.

## Reference Specs

Read before processing:
- Frontmatter: ${CLAUDE_PLUGIN_ROOT}/references/frontmatter-spec.md
- Vault structure: ${CLAUDE_PLUGIN_ROOT}/references/vault-structure.md

## Workflow

### 1. Scan Inbox

Parse the target argument to find files. If no target specified, default to all .md files in 0_inbox/.
Use Glob to expand patterns. Count the files found.

If 0_inbox/ is empty or no files match, inform the user and stop.

### 2. Route by Volume

- **≤10 files** → process directly in current conversation (Section 3)
- **>10 files** → batch dispatch via zet-worker agents (Section 4)

### 3. Direct Processing (≤10 files)

For each file:

**a. Read and Analyze**
- Read full content
- Determine source type: original (user-written) / web-clip (URLs, clipped formatting) / import (from other tools, has existing frontmatter)
- Determine created date: filename pattern (e.g. 20260114) > existing frontmatter > file mtime

**b. Atomize**
- Identify independent concepts in the content
- Multiple unrelated topics → split into separate notes
- Single coherent topic → keep as one note
- Each resulting note must be self-contained

**c. Rewrite**
- Reformulate in clear prose, preserving all core information
- Maintain original language (Chinese stays Chinese, English stays English)
- Improve structure: add headings, clean formatting, fix markdown

**d. Generate Frontmatter**
- id: YYYYMMDDHHmm timestamp (increment minutes for splits from same source)
- title, tags, summary, source, created, processed (today)
- Follow ${CLAUDE_PLUGIN_ROOT}/references/frontmatter-spec.md

**e. Build Links**
- Search 1_zettel/ using Grep for semantically related existing notes
- Add `## Links` section with contextual wikilinks
- Every new note must link to ≥1 existing note
- Format: `- Related to [[note-title]]: explanation of connection`
- Prefer cross-domain connections over obvious same-topic links

**f. Write and Move**
- Write to 1_zettel/YYYY-MM/<slug>.md (create YYYY-MM directory if needed)
- Move images/attachments to 4_assets/, update references to `![[image.png]]`
- Delete source file from 0_inbox/

### 4. Batch Dispatch (>10 files)

Split files into batches of ~10. For each batch, dispatch a zet-worker agent with the file list as prompt input. Workers share the working directory.

Workers handle: read → atomize → rewrite → frontmatter → build links → write to 1_zettel/ → move images.
Workers skip: MOC updates, git commit, inbox deletion.

After all workers complete, proceed to Section 5.
Then delete all processed source files from 0_inbox/.

### 5. Update MOCs

Scan all newly created notes in 1_zettel/. For each tag that appears in ≥3 total notes across 1_zettel/:

- If a MOC exists in 2_maps/ for that topic → read it, append new entries with one-line descriptions, update note_count and last_updated
- If no MOC exists → create one in 2_maps/<topic>.md with proper frontmatter
- Add "Related Maps" links between MOCs that share notes

MOC frontmatter follows ${CLAUDE_PLUGIN_ROOT}/references/frontmatter-spec.md (type: map, note_count, last_updated).

### 6. Commit

```bash
git add 1_zettel/ 2_maps/ 4_assets/
git commit -m "zet: ingest N files, created M notes"
```

### 7. Report

Display to user:
- Files processed from inbox
- Atomic notes generated (may exceed file count if splitting occurred)
- Links created
- MOCs created or updated
- Any files that could not be processed (with reason)
```

- [ ] **Step 2: Commit**

```bash
git add skills/zet-ingest/
git commit -m "feat: add zet-ingest skill for inbox processing"
```

---

### Task 5: Create zet-query Skill

Knowledge base Q&A — the "thinking stage."

**Invoke:** `plugin-dev:skill-development` for SKILL.md format.

**Files:**
- Create: `skills/zet-query/SKILL.md`

- [ ] **Step 1: Write zet-query SKILL.md**

Write `skills/zet-query/SKILL.md`:

```markdown
---
name: zet-query
description: >-
  This skill should be used when the user asks to "search knowledge base", "query notes",
  "zet query", "find in my notes", "what did I write about", "search my notes",
  "find notes about", "what do I know about", or wants to ask questions against their
  Zettelkasten knowledge base. Supports quick (MOC + index only) and deep (reads full notes) modes.
user-invocable: true
arguments:
  - name: question
    description: "The question to query against the knowledge base"
    required: true
  - name: depth
    description: "Query depth: quick (MOC + grep only) | deep (reads full notes). Default: deep"
    required: false
---

# Zettelkasten Query — Knowledge Base Q&A

Answer questions by navigating the Zettelkasten through MOCs and note links. This is the "thinking stage" — where the user engages with their accumulated knowledge.

## Reference Specs

- Frontmatter: ${CLAUDE_PLUGIN_ROOT}/references/frontmatter-spec.md
- Vault structure: ${CLAUDE_PLUGIN_ROOT}/references/vault-structure.md

## Workflow

### 1. Read MOC Index

Read all MOC files in 2_maps/ to build a topic overview. Identify which MOCs are relevant to the question based on titles and content.

If 2_maps/ is empty, skip to step 2 and rely entirely on Grep.

### 2. Locate Relevant Notes

Use multiple strategies to find relevant content:

- **MOC navigation**: Follow links from relevant MOCs to 1_zettel/ notes
- **Keyword search**: Use Grep to search 1_zettel/ for question keywords and related terms
- **Link traversal**: When reading a relevant note, follow its `## Links` section to discover connected notes

Collect a set of candidate notes (aim for 5-20 depending on topic breadth).

### 3. Read Notes

Based on depth parameter:

- **quick**: Read only the frontmatter (title, summary, tags) of candidate notes. Synthesize from summaries.
- **deep** (default): Read full content of the most relevant candidate notes (up to ~15). Follow links to read additional notes if needed for completeness.

### 4. Synthesize Answer

Compose a structured answer that:

- Directly addresses the question
- Cites specific notes using wikilinks: [[note-title]]
- Identifies gaps — topics the knowledge base doesn't cover
- Suggests related notes the user might want to explore
- Maintains the language of the question (Chinese question → Chinese answer)

### 5. Save Output

Save the answer to 3_output/YYYY-MM-DD-<slug>.md with frontmatter:

```yaml
---
title: "Brief question summary"
query: "Original question text"
date: YYYY-MM-DD
sources: ["1_zettel/path/to/note1.md", "1_zettel/path/to/note2.md"]
---
```

Inform the user of the output file location.

### 6. Suggest Follow-ups

Based on the query results, suggest:
- Related questions the user might want to explore
- Notes that are tangentially related but might spark new connections
- Gaps in the knowledge base that could be filled
```

- [ ] **Step 2: Commit**

```bash
git add skills/zet-query/
git commit -m "feat: add zet-query skill for knowledge base Q&A"
```

---

### Task 6: Create zet-lint Skill

Health check — detect structural problems.

**Invoke:** `plugin-dev:skill-development` for SKILL.md format.

**Files:**
- Create: `skills/zet-lint/SKILL.md`

- [ ] **Step 1: Write zet-lint SKILL.md**

Write `skills/zet-lint/SKILL.md`:

```markdown
---
name: zet-lint
description: >-
  This skill should be used when the user asks to "check knowledge base", "zet lint",
  "vault health", "any broken links", "check frontmatter", "find orphan notes",
  "what's wrong with the vault", "knowledge base health", or wants a structural
  health check of their Zettelkasten.
user-invocable: true
---

# Zettelkasten Lint — Health Check

Scan the knowledge base for structural problems: orphan notes, broken links, incomplete frontmatter, MOC gaps.

## Reference Specs

- Frontmatter: ${CLAUDE_PLUGIN_ROOT}/references/frontmatter-spec.md
- Vault structure: ${CLAUDE_PLUGIN_ROOT}/references/vault-structure.md

## Checks

Run all checks below, collecting issues into three categories: errors, warnings, suggestions.

### 1. Broken Links

Scan all .md files in 1_zettel/ and 2_maps/ for wikilinks `[[...]]`.
For each wikilink, verify the target note exists somewhere in 1_zettel/ or 2_maps/.
Report any links pointing to non-existent notes.

**Category**: Error

### 2. Orphan Notes

Find notes in 1_zettel/ that have:
- Zero outbound wikilinks in their `## Links` section, OR
- Zero inbound wikilinks (no other note links to them)

Use Grep to search for `[[note-title]]` across all files to detect inbound links.

**Category**: Warning (zero outbound), Error (zero inbound — note is completely disconnected)

### 3. Frontmatter Completeness

Read ${CLAUDE_PLUGIN_ROOT}/references/frontmatter-spec.md for required field lists.

For each file in 1_zettel/:
- Check all 7 required frontmatter fields are present: id, title, created, processed, source, tags, summary
- Check `## Links` section exists in the body

For each file in 2_maps/:
- Check all 4 required fields: title, type, note_count, last_updated

**Category**: Warning

### 4. MOC Coverage

Count how many notes in 1_zettel/ are referenced by at least one MOC in 2_maps/.
Report notes not referenced by any MOC.

**Category**: Suggestion (if the note has tags that match an existing MOC but isn't listed)

### 5. Tag-MOC Alignment

Collect all tags from 1_zettel/ frontmatter. For tags with ≥3 notes:
- Check if a corresponding MOC exists in 2_maps/
- If not, suggest creating one

**Category**: Suggestion

### 6. Empty Files

Find files in 1_zettel/ and 2_maps/ with no content (only frontmatter or completely empty).

**Category**: Error

### 7. Stale MOC Counts

For each MOC in 2_maps/, count actual inbound note links and compare to the `note_count` frontmatter field.
Report mismatches.

**Category**: Warning

## Output

Generate 3_output/lint-report-YYYY-MM-DD.md:

```markdown
# Zettelkasten Lint Report — YYYY-MM-DD

## Summary
- Total notes: N
- Total MOCs: N
- Errors: N
- Warnings: N
- Suggestions: N

## Errors
- [list each error with file path and description]

## Warnings
- [list each warning]

## Suggestions
- [list each suggestion]
```

## Auto-Fix

After presenting the report, offer to auto-fix:
- Create missing MOCs for tags with ≥3 notes
- Update stale MOC note_counts
- Add missing `## Links` sections (with placeholder for user to fill)

Ask user for confirmation before applying fixes. If fixes are applied, commit:

```bash
git add 1_zettel/ 2_maps/
git commit -m "zet: lint auto-fix — N issues resolved"
```
```

- [ ] **Step 2: Commit**

```bash
git add skills/zet-lint/
git commit -m "feat: add zet-lint skill for knowledge base health check"
```

---

### Task 7: Update CLAUDE.md and README.md

Project documentation reflecting the new Zettelkasten architecture.

**Files:**
- Rewrite: `CLAUDE.md`
- Rewrite: `README.md`

- [ ] **Step 1: Rewrite CLAUDE.md**

Replace entire `CLAUDE.md` with:

```markdown
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
```

- [ ] **Step 2: Rewrite README.md**

Replace entire `README.md` with:

```markdown
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
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md README.md
git commit -m "docs: rewrite CLAUDE.md and README.md for Zettelkasten plugin"
```

---

### Task 8: Validate Plugin Structure

Final validation to ensure everything loads correctly.

**Invoke:** `plugin-dev:plugin-validator` agent to check plugin structure.

**Files:** None (read-only validation)

- [ ] **Step 1: Run plugin-validator**

Invoke `plugin-dev:plugin-validator` agent to verify:
- `.claude-plugin/plugin.json` exists and is valid
- All skills have `SKILL.md` with valid frontmatter (name, description)
- Agent has valid frontmatter (name, description, model, color)
- All `${CLAUDE_PLUGIN_ROOT}` references in skills/agent point to existing files
- No orphan files or broken internal references

- [ ] **Step 2: Run skill-reviewer on each skill**

Invoke `plugin-dev:skill-reviewer` agent on each skill to verify:
- Description quality (third-person, specific trigger phrases)
- Body writing style (imperative/infinitive form)
- Progressive disclosure (lean SKILL.md, details in references/)
- Referenced files exist

- [ ] **Step 3: Fix any issues found**

Address any validation errors or warnings. Commit fixes:

```bash
git add -A
git commit -m "fix: address plugin validation feedback"
```

- [ ] **Step 4: Final verification**

```bash
ls -la .claude-plugin/plugin.json
ls skills/*/SKILL.md
ls agents/*.md
ls references/*.md
```

Expected output:
```
.claude-plugin/plugin.json
skills/zet-ingest/SKILL.md
skills/zet-query/SKILL.md
skills/zet-lint/SKILL.md
agents/zet-worker.md
references/frontmatter-spec.md
references/vault-structure.md
```

---

## Self-Review Checklist

- [x] **Spec coverage**: All 4 components (zet-ingest, zet-query, zet-lint, zet-worker) have dedicated tasks. Frontmatter spec, vault structure, atomization rules, link building rules, MOC maintenance rules all covered. Plugin.json, CLAUDE.md, README.md, .gitignore all addressed.
- [x] **Placeholder scan**: No TBD/TODO. All file contents are complete. All paths are exact.
- [x] **Type consistency**: Frontmatter field names consistent across spec, references, skills, and agent: `id`, `title`, `created`, `processed`, `source`, `tags`, `summary` (permanent notes); `title`, `type`, `note_count`, `last_updated` (MOCs); `title`, `query`, `date`, `sources` (output).
