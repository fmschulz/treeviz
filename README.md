# TreeViz

TreeViz is a browser-based viewer for phylogenetic trees, metadata tracks, and
publication figures. It reads Newick, Nexus, TSV and CSV metadata, and
`.treeviz.json` sessions, and runs at
[treeviz.newlineages.com](https://treeviz.newlineages.com/).

![Radial tree of life with phyla collapsed to wedges and coloured by domain](docs/assets/gallery/tree-of-life-phylum-wedges.png)

This repository holds the public documentation, the examples, the issue
tracker, and the agent skill. The app source is not published here.

## Documentation

The site is at [fmschulz.github.io/treeviz](https://fmschulz.github.io/treeviz/).
Start with [Getting started](docs/GETTING_STARTED.md), then the
[Examples](docs/EXAMPLES.md) page for complete figures with their settings, the
[Tree styling](docs/STYLING.md) reference for every option, and the
[Browser API](docs/API.md) for automation. To serve the pages locally:

```bash
pip install -r requirements-docs.txt
mkdocs serve
```

## Python Package

The PyPI distribution is `treeviz-phylo`; the import name is `treeviz`.

```bash
pip install treeviz-phylo
```

```python
from treeviz import build_session, save_session, validate_session, view_session

tree = "(A:0.1,B:0.2,(C:0.3,D:0.4):0.5);"
metadata = [
    {"id": "A", "group": "alpha", "value": 1.2},
    {"id": "B", "group": "alpha", "value": 0.8},
    {"id": "C", "group": "beta", "value": 2.1},
    {"id": "D", "group": "beta", "value": 1.6},
]
tracks = [
    {"kind": "color_strip", "column_key": "group", "title": "Group"},
    {"kind": "gradient", "column_key": "value", "title": "Value"},
]

session = build_session(tree, metadata=metadata, tracks=tracks, row_key_column="id")
validate_session(session)
save_session(session, "example.treeviz.json")
view_session(session, open_browser=False).url
```

See [Python package](docs/PYTHON.md).

## Agent Skill

[.agents/skills/treeviz-agent/SKILL.md](.agents/skills/treeviz-agent/SKILL.md)
is for coding agents that open TreeViz, import data, configure tracks, tune
layouts, and export figures through the hosted browser API:

```text
https://treeviz.newlineages.com/?api=1
https://treeviz.newlineages.com/?mode=headless&api=1
```

## Compatibility

The hosted app reports version 0.8.2 through
[`version.json`](https://treeviz.newlineages.com/version.json). The
[`treeviz-phylo` 0.6.0](https://pypi.org/project/treeviz-phylo/) package
writes sessions the app opens. Its bundled schema lacks fields the app writes
(the view fields `showNodeCircles`, `collapsedWedgeFillAttribute`,
`collapsedWedgeFillOpacity`, `collapsedWedgeLabelDeclutter`,
`collapsedWedgeLabelOrientation` and `collapsedWedgeFill = "attribute"`, and
the top-level `legends` and
`attributeLabels`), so `validate_session` rejects app-saved sessions that use
them; see [Schema Compatibility](docs/PYTHON.md#schema-compatibility).
Sessions written by earlier releases load and are migrated on open.

## Issues

Use GitHub issues here for documentation, Python package usage, metadata
import questions, and agent workflow reports.
