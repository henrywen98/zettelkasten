---
name: zet-lint
description: >-
  This skill should be used when the user asks to "check knowledge base", "zet lint",
  "vault health", "any broken links", "check frontmatter", "find orphan notes",
  "what's wrong with the vault", "knowledge base health", or wants a structural
  health check of their Zettelkasten.
---

# Zettelkasten Lint — Health Check

Scan the knowledge base for structural problems: orphan notes, broken links, incomplete frontmatter, MOC gaps.

## Implementation Notes

- Scan `1_zettel/` **recursively** for all `.md` files (not just one subdirectory)
- Scan `2_maps/` dynamically with Glob — never hardcode MOC filenames
- When writing helper scripts, use the **Write tool** to create a `.py` file, then run it with Bash. Do NOT use Bash heredoc or inline Python — the `!=` operator gets escaped to `\!=` in heredoc, causing SyntaxError.

## Reference Specs

- Frontmatter: ${CLAUDE_PLUGIN_ROOT}/references/frontmatter-spec.md
- Vault structure: ${CLAUDE_PLUGIN_ROOT}/references/vault-structure.md
- MOC rules: ${CLAUDE_PLUGIN_ROOT}/references/moc-rules.md

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
- Zero inbound wikilinks (no other note links to them), OR
- **Effective inbound < 1** (only inbound links come from MOCs in 2_maps/, not from peer notes) — these are indexed but not knowledge-connected

Use Grep to search for `[[note-title]]` across all files to detect inbound links. When counting "effective" inbound, exclude links from 2_maps/ files.

Check 2 only covers peer-to-peer links. MOC coverage issues belong to Check 4.

**Category**: Warning (zero outbound, or only-MOC inbound), Error (zero inbound — completely disconnected)

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

Collect all tags from 1_zettel/ frontmatter. **Normalize tags to lowercase kebab-case before counting** (per frontmatter-spec.md Tag Normalization — `AI` and `ai` count as the same tag). For normalized tags with ≥3 notes:
- Check if a corresponding MOC exists in 2_maps/ (match case-insensitively per moc-rules.md)
- If not, suggest creating one

**Category**: Suggestion

### 6. Empty Files

Find files in 1_zettel/ and 2_maps/ with no content (only frontmatter or completely empty).

**Category**: Error

### 7. Stale MOC Counts

For each MOC in 2_maps/, count the actual `- [[` entries under `## Notes` and compare to the `note_count` frontmatter field (per moc-rules.md — note_count must equal the count of `- [[` lines, not inbound links from other files).
Report mismatches.

**Category**: Warning

### 8. Tag Case Consistency

Collect all tags from 1_zettel/ frontmatter. Group tags by their lowercase form. Report any tag that appears in multiple case variants (e.g. `AI` in 15 notes vs `ai` in 15 notes).

Also check for non-kebab-case tags: spaces, underscores, slashes, uppercase letters. Report any tag that violates the lowercase-kebab-case rule per frontmatter-spec.md Tag Normalization.

**Category**: Warning (case variants exist), Error (if variants merged would reach ≥3 notes but no MOC exists)

### 9. Broken Image References

Scan all .md files in 1_zettel/ for image references matching:
- `![[filename.png]]` (Obsidian wikilink, including `![[Pasted image ...]]`)
- `![alt](path)` (standard markdown)

For each referenced image, verify the file exists in `4_assets/`. Report missing images.

**Category**: Error

### 10. Near-Duplicate Notes

Scan all notes in 1_zettel/. Flag potential duplicates by checking:
- Notes whose titles are exactly identical
- Notes where one title is a substring of another

For each pair of suspected duplicates, report both file paths and their titles for user review.

**Category**: Suggestion

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

## Relink Candidates
- Notes with 0 peer inbound links (N):
  - note-a.md
  - note-b.md
- Notes with only-MOC inbound links (N):
  - note-c.md
- Estimated backlinks to add: N
```

## Auto-Fix

After presenting the report, offer to auto-fix:
- **Tag normalization** (fixes Check 8): batch-rewrite all notes' frontmatter tags to lowercase-kebab-case per frontmatter-spec.md. Show preview before applying (e.g. "Will normalize `AI` → `ai` in 15 notes").
- **MOC filename normalization** (fixes Check 8): rename `2_maps/` files to lowercase kebab-case (e.g. `AI.md` → `ai.md`). On macOS APFS (case-insensitive), use two-step rename: `git mv AI.md tmp.md && git mv tmp.md ai.md`. Do NOT modify wikilink text content — Obsidian wikilinks are case-insensitive.
- **Create missing MOCs** (fixes Check 5): for normalized tags with ≥3 notes, create MOC per moc-rules.md
- **Update stale MOC note_counts** (fixes Check 7): recount from actual `- [[` entries per moc-rules.md, also append missing note entries and update Related Maps cross-links
- Add missing `## Links` sections (with placeholder for user to fill)
- **Relink orphan/weak-linked notes** (fixes Check 2): for each note with zero peer inbound or only-MOC inbound links, find 1-3 best candidate notes and add contextual backlinks to their `## Links` section. Three-level candidate search:
  1. **Reciprocal** `[reciprocal]` — outbound target A→B exists, add B→A (highest confidence, no search needed)
  2. **Tag match** `[tag-match]` — same tag, different note (deterministic)
  3. **Slug match** `[slug-match]` — 2-3 meaningful slug segments via Grep (only if levels 1-2 yield nothing, search terms ≤ 3)
  - Preview shows target's current link count and confidence source
  - Per-operation limit: 3 new backlinks per target (5 for hub nodes with >5 outbound links)
  - Global cap: target `## Links` total ≤ 10 entries (skip if exceeded)
  - Idempotent — dedup by `[[slug]]` only, existing links are not duplicated
  - Preview format example:
    ```
    1. sydney-tap-water-safety.md (0 inbound → 1)
       + Add to wolli-creek-rental-arrangement.md (current: 3 links) [reciprocal]:
         "Sydney tap water safety is relevant to daily life in Wolli Creek"
    ```

Ask user for confirmation before applying fixes. If fixes are applied, commit:

```bash
git add 1_zettel/ 2_maps/
git commit -m "zet: lint auto-fix — N issues resolved"
```
