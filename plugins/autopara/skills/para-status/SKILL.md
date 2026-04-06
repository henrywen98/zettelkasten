---
name: para-status
description: >-
  Quick overview of knowledge base stats: article counts, tag distribution, inbox backlog, recent activity.
  Trigger when user says "vault status", "vault stats", "how many in inbox", "how big is the vault", "recent archives".
user-invocable: true
arguments:
  - name: vault_path
    description: "Obsidian vault path"
    required: true
---

# PARA Status — Knowledge Base Stats

Quick overview of the current vault state.

## Stats

1. **File Counts**
   - 0_inbox/ pending count
   - 3_archive/ archived count
   - 1_wiki/concepts/ concept article count
   - 1_wiki/topics/ topic article count
   - 1_wiki/viz/ visualization count
   - 2_output/ query output count

Use Bash to count:
```bash
VAULT="<vault_path>"  # from vault_path argument
echo "inbox: $(find "$VAULT/0_inbox" -name '*.md' 2>/dev/null | wc -l)"
echo "archive: $(find "$VAULT/3_archive" -name '*.md' 2>/dev/null | wc -l)"
echo "concepts: $(find "$VAULT/1_wiki/concepts" -name '*.md' 2>/dev/null | wc -l)"
echo "topics: $(find "$VAULT/1_wiki/topics" -name '*.md' 2>/dev/null | wc -l)"
echo "viz: $(find "$VAULT/1_wiki/viz" -name '*.md' 2>/dev/null | wc -l)"
echo "output: $(find "$VAULT/2_output" -name '*.md' 2>/dev/null | wc -l)"
```

2. **Tag Distribution** (Top 20)
   - Read 1_wiki/_tags.md, show the 20 most used tags and their file counts

3. **Recent Activity**
   - Last 5 archived files
   - Last 5 updated wiki articles

4. **Health Overview**
   - Inbox backlog count
   - Orphan page count (3_archive/ files not referenced by 1_wiki/)
   - If backlog > 10 or orphans > 20, suggest running /para lint

Present to user in table format.
