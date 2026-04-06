---
name: para-query
description: >-
  Ask questions against the knowledge base, AI retrieves relevant notes and generates structured answers.
  Trigger when user says "search knowledge base", "query notes", "find in my notes", "what did I write about...", "find notes about...", "search my notes".
  Supports quick (index only) and deep (read originals) depth levels.
user-invocable: true
arguments:
  - name: vault_path
    description: "Obsidian vault path"
    required: true
  - name: question
    description: "The question to query"
    required: true
  - name: depth
    description: "Query depth: quick (fast, index only) | deep (thorough, reads originals)"
    required: false
---

# PARA Query — Knowledge Base Q&A

Answer user questions based on 1_wiki/ and 3_archive/ content.

## Workflow

### 1. Read Indexes

Read the following files to build a global overview:
- 1_wiki/_index.md — all articles list
- 1_wiki/_tags.md — tag index

### 2. Locate Relevant Content

Based on question keywords:
- Match relevant articles in _index.md
- Match relevant tags in _tags.md
- Use Grep to search 3_archive/ and 1_wiki/ for keywords

### 3. Deep Read

Based on the depth parameter:
- **quick** (default): only read matching articles in 1_wiki/concepts/ and 1_wiki/topics/
- **deep**: also read original files in 3_archive/

### 4. Generate Answer

Synthesize all read content into a structured answer.

### 5. Save Output

Save the answer to 2_output/YYYY-MM-DD-<slug>.md:

```yaml
---
title: <brief question summary>
query: "<original question>"
date: YYYY-MM-DD
sources: [list of referenced file paths]
---
```

Inform the user of the output file location, and ask if they want to archive this output into 1_wiki/ (as a new topic or concept article).
