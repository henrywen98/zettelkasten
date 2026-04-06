---
name: zet-ingest
description: >-
  This skill should be used when the user asks to "process inbox", "ingest notes",
  "organize inbox", "zet ingest", "digest notes", "process new notes",
  "clean up inbox", "handle new materials", "run zettelkasten", or has new files in 0_inbox/ to process.
  Orchestrates Zettelkasten ingestion: scans inbox, dispatches zet-worker agents in sequential
  batches, updates MOCs, and commits. The most frequently used daily command.
user-invocable: true
arguments:
  - name: target
    description: "File path or glob pattern, e.g. 0_inbox/*.md or a specific filename. Omit to process all .md files in 0_inbox/"
    required: false
---

# Zettelkasten Ingest — Orchestrator

Pure orchestrator. All file processing is delegated to zet-worker agents. This skill handles scanning, batching, dispatching, MOC updates, and commits.

## Workflow

### 1. Scan Inbox

Parse the target argument to find files. If no target specified, default to all .md files in 0_inbox/.
Use Glob to expand patterns. Count the files found.

If 0_inbox/ is empty or no files match, inform the user and stop.

### 2. Batch and Dispatch

Split all files into batches of 10 (last batch may be smaller). Process batches **one at a time, in order**.

**For each batch:**

1. Dispatch a zet-worker agent with the batch file list as prompt input
2. Wait for the worker to complete and collect its output (files processed, notes created, note paths)
3. Delete processed source files from 0_inbox/
4. Update MOCs for notes created in this batch (Section 3)
5. Commit this batch (Section 4)
6. Report batch progress: "Batch N/M complete: processed X files, created Y notes"

**Why sequential:** Each batch commits before the next begins. Batch N+1 can link to notes from all prior batches, improving link quality progressively. User may interrupt between batches — all prior work is preserved.

### 3. Update MOCs

Scan newly created notes from the current batch. For each tag that appears in ≥3 total notes across 1_zettel/:

- If a MOC exists in 2_maps/ for that topic → read it, append new entries with one-line descriptions, update note_count and last_updated
- If no MOC exists → create one in 2_maps/<topic>.md with proper frontmatter
- Add "Related Maps" links between MOCs that share notes

MOC frontmatter follows ${CLAUDE_PLUGIN_ROOT}/references/frontmatter-spec.md (type: map, note_count, last_updated).

### 4. Commit

```bash
git add 1_zettel/ 2_maps/ 4_assets/
git commit -m "zet: ingest N files, created M notes (batch X/Y)"
```

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
