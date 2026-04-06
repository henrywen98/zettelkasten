---
name: para-lint
description: >-
  Knowledge base health check: scan for broken links, orphan pages, tag inconsistencies, missing frontmatter.
  Trigger when user says "check knowledge base", "vault health", "any broken links", "check frontmatter", "what's wrong with the vault".
user-invocable: true
arguments:
  - name: vault_path
    description: "Obsidian vault path"
    required: true
---

# PARA Lint — Knowledge Base Health Check

Scan the knowledge base and report data integrity issues.

**Reference specs:**
- Frontmatter: ${CLAUDE_PLUGIN_ROOT}/references/frontmatter-spec.md
- Vault structure: ${CLAUDE_PLUGIN_ROOT}/references/vault-structure.md

## Checks

### 1. Broken Link Check
- Scan all md files for image links (![](path) and ![[path]])
- Verify link targets exist
- Scan 1_wiki/ files' sources field, verify referenced 3_archive/ files exist

### 2. Orphan Page Check
- Find 3_archive/ files not referenced by any 1_wiki/ article
- These files need to be compiled into 1_wiki/

### 3. Frontmatter Completeness
- Read ${CLAUDE_PLUGIN_ROOT}/references/frontmatter-spec.md for required field lists
- Check 3_archive/ and 1_wiki/ files meet their respective required field requirements
- List files with missing fields

### 4. Tag Consistency
- Compare _tags.md index with actual tags in files
- Find tags in the index but not in files (ghost tags)
- Find tags in files but not in the index (missing tags)

### 5. Concept Coverage
- Count concepts referenced in 3_archive/ file frontmatter
- Check whether corresponding 1_wiki/concepts/ articles exist
- Suggest creating articles for high-frequency but missing concepts

## Output

Generate 2_output/lint-report-YYYY-MM-DD.md, categorized by severity:

- **Errors**: broken links, empty files, file count mismatch
- **Warnings**: missing frontmatter fields, orphan pages
- **Suggestions**: new concept candidates, tag cleanup

Ask user whether to auto-fix fixable issues (e.g., update indexes, create missing concept articles).
