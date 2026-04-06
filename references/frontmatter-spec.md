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
