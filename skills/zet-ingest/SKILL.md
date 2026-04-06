---
name: zet-ingest
description: >-
  This skill should be used when the user asks to "process inbox", "ingest notes",
  "organize inbox", "zet ingest", "digest notes", "process new notes",
  "clean up inbox", "handle new materials", "run zettelkasten", or has new files in 0_inbox/ to process.
  Orchestrates Zettelkasten ingestion: scans inbox, dispatches zet-worker agents in sequential
  batches, updates MOCs, and commits. The most frequently used daily command.
  Accepts optional target argument: file path or glob pattern (e.g. 0_inbox/*.md). Omit to process all .md files in 0_inbox/.
---

# Zettelkasten Ingest — Orchestrator

Pure orchestrator. All file processing is delegated to zet-worker agents. This skill handles scanning, batching, dispatching, MOC updates, and commits.

## Workflow

### 1. Scan Inbox

Parse the target argument to find files. If no target specified, default to all .md files in 0_inbox/ **recursively** (including all subdirectories). Use Glob pattern `0_inbox/**/*.md` to find all nested files.

If the user provides a target (file path or glob), expand it with Glob. Count the files found.

If 0_inbox/ is empty or no files match, inform the user and stop.

### 2. Batch and Dispatch

Split all files into batches of 10 (last batch may be smaller). Process batches **one at a time, in order**.

**For each batch:**

1. Dispatch a zet-worker agent with the batch file list as prompt input
2. Wait for the worker to complete and collect its output (files processed, notes created, note paths)
3. Delete processed source files from 0_inbox/ — always double-quote paths (`rm -- "<path>"`), use `--` to prevent `-` filenames from being parsed as flags. If `rm` fails for a file, log the failure and continue with remaining files — do not abort the batch.
4. Update MOCs for notes created in this batch (Section 3)
5. Commit this batch (Section 4)
6. Report batch progress: "Batch N/M complete: processed X files, created Y notes"

**Why sequential:** Each batch commits before the next begins. Batch N+1 can link to notes from all prior batches, improving link quality progressively. User may interrupt between batches — all prior work is preserved.

### 3. Update MOCs

Follow ${CLAUDE_PLUGIN_ROOT}/references/moc-rules.md for all MOC operations.

**3a. Collect tags from the entire vault (not just current batch)**

Use Grep to search all `1_zettel/` files for `tags:` lines in one pass — do NOT read each file's frontmatter individually. Normalize all tags to lowercase kebab-case per frontmatter-spec.md, then count how many notes use each normalized tag.

**3b. Create or update MOCs**

For each normalized tag with ≥3 notes, follow moc-rules.md to create or update the MOC. Key rules:
- Match existing MOCs case-insensitively (Glob `2_maps/*.md`, lowercase filename comparison)
- When updating, append missing note entries and **recount note_count from actual `- [[` lines** (never increment)
- When creating, use normalized tag as filename (e.g. `2_maps/ai.md`)

**3c. Update Related Maps cross-links**

After all MOCs are updated, scan for MOCs that share notes and add missing cross-links per moc-rules.md.

### 4. Commit

```bash
git add 1_zettel/ 2_maps/ 4_assets/
git add -u 0_inbox/
git commit -m "zet: ingest N files, created M notes (batch X/Y)"
```

The `git add -u 0_inbox/` stages deletions of processed inbox files so git tracks the cleanup.

For single-batch runs, omit batch numbering:

```bash
git commit -m "zet: ingest N files, created M notes"
```

### 5. Report

After all batches complete, display summary:
- Total files processed from inbox
- Total atomic notes generated (may exceed file count if splitting occurred)
- Total links created
- MOCs created or updated
- Any files that could not be processed (with reason)
