---
name: para-ingest
description: >-
  Process new files in 0_inbox/, archive to 3_archive/ and incrementally compile into 1_wiki/.
  Trigger when user says "process notes", "organize inbox", "archive this", "digest new notes", "process inbox", "new notes to process".
  This is the most frequently used daily command.
user-invocable: true
arguments:
  - name: target
    description: "File path or glob pattern to process, e.g. 0_inbox/*.md or a specific filename. Omit to process all .md files in 0_inbox/"
    required: false
---

# PARA Ingest — Process Inbox Files

Archive files from 0_inbox/ to 3_archive/ and update 1_wiki/.

## Workflow

### 1. Locate Files

Parse the target argument to find the file list. Expand glob patterns if provided.
Confirm the file list with the user.

### 2. Process Each File

For each file:

**a. Analyze Content**
- Read the full file
- Determine source type (original / web-clip / import)
- Generate frontmatter: title, tags, summary, concepts
- Determine created date (extract from filename > frontmatter > file mtime)
- Determine target path: 3_archive/YYYY-MM/<slug>.md

**b. Write Frontmatter**
- Insert YAML frontmatter at the top of the file
- Follow the spec in ${CLAUDE_PLUGIN_ROOT}/references/frontmatter-spec.md

**c. Move File**
- Move to 3_archive/YYYY-MM/ directory
- Move associated images/attachments to 4_assets/
- Run relink to update links:
```bash
cd "${CLAUDE_PLUGIN_ROOT}/scripts"
uv run relink.py "<file>" "<old_prefix>" "../4_assets/"
```

**d. Update Wiki**
- Read 1_wiki/_index.md, append new entry
- Read 1_wiki/_tags.md, update tag index
- For each concept:
  - If 1_wiki/concepts/<concept>.md exists → append source to sources list
  - If it doesn't exist and AI judges it worth creating → create concept article

### 3. Commit

```bash
git add -A
git commit -m "para: ingest N files from inbox"
```

### 4. Report

Show the user the results:
- How many files processed
- Which concepts were generated/updated
- Which tags were added
