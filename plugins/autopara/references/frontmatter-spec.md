# Frontmatter Spec

## Archive Files (under 3_archive/)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | yes | Article title |
| created | date (YYYY-MM-DD) | yes | Original creation date |
| archived | date (YYYY-MM-DD) | yes | Archive date |
| tags | string[] | yes | Tag list |
| summary | string | yes | One-line summary |
| concepts | string[] | yes | Associated concept list (maps to 1_wiki/concepts/ articles) |
| source | enum: original, web-clip, import | yes | Source type |

## Wiki Articles (under 1_wiki/)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | yes | Concept/topic name |
| type | enum: concept, topic, viz | yes | Article type |
| sources | string[] | yes | Referenced archive file path list |
| related | string[] | yes | Related concepts/topics list |
| last_compiled | date (YYYY-MM-DD) | yes | Last compilation date |

## Query Output (under 2_output/)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | yes | Brief question summary |
| query | string | yes | Original query question |
| date | date (YYYY-MM-DD) | yes | Query date |
| sources | string[] | yes | Referenced file path list |
