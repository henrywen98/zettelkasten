---
name: para-viz
description: >-
  Generate visualizations from knowledge base content: Marp slides, Mermaid diagrams, Matplotlib charts.
  Trigger when user says "generate slides", "visualize", "knowledge graph", "make a presentation", "draw a relationship diagram", "generate charts", "visualize".
user-invocable: true
arguments:
  - name: vault_path
    description: "Obsidian vault path"
    required: true
  - name: topic
    description: "Topic or question"
    required: true
  - name: format
    description: "Output format: marp | mermaid | matplotlib (default: marp)"
    required: false
---

# PARA Viz — Knowledge Base Visualization

Generate visual outputs from knowledge base content.

## Formats

### Marp (default)
Generate Marp-formatted markdown slides, saved to 1_wiki/viz/<slug>.md.

Marp file format:
```yaml
---
marp: true
theme: default
paginate: true
---
```

Best for: topic overviews, study notes, knowledge sharing

### Mermaid
Generate Mermaid diagrams embedded in a markdown file.

Best for: concept relationship diagrams, flowcharts, knowledge graphs

### Matplotlib
Generate a temporary Python matplotlib script, run it to output PNG to 4_assets/viz/.

AI generates and executes the script at runtime:
```bash
cd "<vault_path>"
uv run /tmp/para_viz_<slug>.py
```

Best for: tag distribution stats, timelines, word frequency analysis

## Workflow

1. Read 1_wiki/_index.md and 1_wiki/_tags.md to locate relevant content
2. Read relevant 1_wiki/ articles and 3_archive/ originals
3. Generate visualization based on format
4. Add wiki frontmatter to generated file (following ${CLAUDE_PLUGIN_ROOT}/references/frontmatter-spec.md):
   - type: viz
   - sources: list of referenced 3_archive/1_wiki/ files
   - related: related concepts
   - last_compiled: today's date
5. Save to 1_wiki/viz/ or 4_assets/viz/
6. Record new viz entry in 1_wiki/_index.md
7. Commit
