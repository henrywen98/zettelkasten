---
name: para-migrate
description: >-
  One-time full migration of an existing Obsidian vault to AutoPARA structure (0_inbox/3_archive/1_wiki/4_assets).
  Trigger when user says "migrate vault", "initialize autopara", "restructure vault", "organize notes from scratch", "vault init".
  Only needed on first use; daily processing uses para-ingest afterwards.
user-invocable: true
arguments:
  - name: vault_path
    description: "Obsidian vault path"
    required: true
---

# PARA Migrate — Full Migration

Migrate an existing Obsidian vault to AutoPARA structure (0_inbox/3_archive/1_wiki/4_assets).

**Prerequisites**: vault has git init + git lfs install, with an initial commit as backup.

**Reference specs:**
- Frontmatter: ${CLAUDE_PLUGIN_ROOT}/references/frontmatter-spec.md
- Vault structure: ${CLAUDE_PLUGIN_ROOT}/references/vault-structure.md

## Migration Flow

Phase 1: Scan (script) → manifest.json
Phase 2: Plan (AI) → migration-plan.json
Phase 3: Execute (teammates) → file migration + frontmatter
Phase 4: Validate (script) → validation-report.md

## Phase 1: Scan

Run the scan script to generate a complete vault inventory:

```bash
cd "${CLAUDE_PLUGIN_ROOT}/scripts"
uv run scan.py "<vault_path>" "<vault_path>/manifest.json"
```

Produces manifest.json. Report stats to user (file count, attachments, size).

## Phase 2: Plan

1. Create target directory structure:

```bash
cd "<vault_path>"
mkdir -p 0_inbox 3_archive 1_wiki/concepts 1_wiki/topics 1_wiki/viz 2_output 4_assets
```

2. Read manifest.json, batch by original folders (~50 file entries per batch)
3. For each batch: read file previews, generate migration-plan fragment:
   - target: destination path (3_archive/YYYY-MM/<slug>.md)
   - frontmatter: AI-generated tags, summary, concepts from preview
   - restructure: whether content needs restructuring (true/false)
4. Merge all fragments into a complete migration-plan.json
5. **Pause for user to review migration-plan.json**

migration-plan.json format:

```json
{
  "actions": [
    {
      "source": "00_Inbox/20260114-2042-SSH Key - henrywen.md",
      "target": "3_archive/2026-01/ssh-key-henrywen.md",
      "frontmatter": {
        "title": "SSH Key Configuration Guide",
        "tags": ["ssh", "devops"],
        "summary": "Complete guide to SSH key generation and configuration",
        "concepts": ["SSH Key Authentication"],
        "source": "original"
      },
      "restructure": false,
      "images": ["img/ssh-1.png"],
      "image_targets": ["4_assets/ssh-1.png"]
    }
  ],
  "concept_candidates": ["SSH Key Authentication", "Docker Deployment", "Git Workflow"],
  "duplicate_groups": [],
  "outdated": []
}
```

## Phase 3: Parallel Execution (teammates)

After user approves:

1. Split migration-plan.json into batches of ~40 actions
2. Dispatch a teammate for each batch (using worktree isolation)
3. Each teammate's task:
   - Read assigned action list
   - For each action:
     a. Read source file in full
     b. Write frontmatter (from plan)
     c. If restructure=true, restructure markdown content
     d. Move to target path
     e. Move associated images to 4_assets/
     f. Run relink to update image links
   - Commit the batch changes when done
4. After all teammates complete, merge back to main branch
5. Clean up old empty directories

Teammate execution template:

```
You are an AutoPARA migration worker. Your task is to process a batch of file migrations.

Vault path: <vault_path>
Relink script path: ${CLAUDE_PLUGIN_ROOT}/scripts/relink.py

Your batch actions (JSON):
<batch_actions>

For each action:
1. Read the source file
2. Write frontmatter at the top (preserve original content)
3. If restructure=true, improve markdown structure (do not lose any information)
4. Create target directory (if it doesn't exist)
5. Move file to target path
6. Move images to image_targets
7. Use relink.py to update links

When all done, commit:
git add -A && git commit -m "migrate: batch N (M files)"
```

## Phase 4: Validate

```bash
cd "${CLAUDE_PLUGIN_ROOT}/scripts"
uv run validate.py "<vault_path>" "<vault_path>/manifest.json"
```

Show the user the validation-report.md content. If issues found, list them and assist with fixes.

## Phase 5: Wiki Compilation (first time)

After validation passes:

1. Read all 3_archive/ file frontmatter
2. Count concept and tag frequencies
3. Generate 1_wiki/concepts/ articles for high-frequency concepts (>= 2 occurrences)
4. Generate 1_wiki/topics/ aggregation pages for high-frequency tags (>= 5 occurrences)
5. Generate 1_wiki/_index.md (all archive files list + summaries)
6. Generate 1_wiki/_tags.md (all tags and their associated files)
7. Commit wiki

## Safety Mechanisms

- Check git status before migration, must have an initial commit
- Pause for confirmation between phases
- Keep manifest.json as rollback reference
- Any phase failure can git reset to the previous commit
