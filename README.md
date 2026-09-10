# TreeViz

TreeViz is a browser-based viewer and editor for phylogenetic trees and
tree-aligned metadata. It reads Newick, CONTree, Nexus, TSV, CSV, and
`.treeviz.json` files; supports rerooting, pruning, collapsing, and styling;
and exports SVG, PNG, PDF, and data files. Tree and metadata processing happens
in the browser.

[Open TreeViz](https://treeviz.newlineages.com/) ·
[Read the documentation](https://fmschulz.github.io/treeviz/) ·
[Browse the examples](https://fmschulz.github.io/treeviz/EXAMPLES/)

![Circular Mirusviricota phylogeny with 18 metadata tracks](docs/assets/gallery/example-1-mirusviricota.svg)

This repository contains the public documentation, example scripts, issue
tracker, and agent skill. The browser app source is maintained separately.

## Browser app

Open [treeviz.newlineages.com](https://treeviz.newlineages.com/), then choose a
hosted example or load a tree from your computer. Add a TSV or CSV table when
you want to align metadata with the leaves. Save a `.treeviz.json` session to
preserve the tree, metadata binding, tracks, edits, and view settings.

The [getting-started tutorial](docs/GETTING_STARTED.md) uses the 1,204-tip
Mirusviricota Extended Data Figure 9 session from
[doi:10.1038/s41564-025-02190-6](https://doi.org/10.1038/s41564-025-02190-6).
The [examples page](docs/EXAMPLES.md) links this session and its SVG figure.

## Python package

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

See the [Python package guide](docs/PYTHON.md) for metadata, notebooks, static
rendering, and schema compatibility.

## Agent skill

The public skill at
[`.agents/skills/treeviz-agent/`](.agents/skills/treeviz-agent/) teaches coding
agents to import data, configure tracks, style clades, inspect diagnostics, tune
layouts, fit circular openings, save views, and export figures through
`window.__treeviz`.

Use the hosted runtime:

```text
https://treeviz.newlineages.com/?api=1
https://treeviz.newlineages.com/?mode=headless&api=1
```

Start with the [agent automation guide](docs/AGENTS.md). The live app also
publishes a compact [agent API entry page](https://treeviz.newlineages.com/agent),
the command schema, the session schema, and the example manifest.

## Build the documentation

```bash
pip install -r requirements-docs.txt
mkdocs serve
```

Run `mkdocs build --strict` before publishing.

## Versions and compatibility

The hosted app reports its build through
[`version.json`](https://treeviz.newlineages.com/version.json). The app and the
Python package have separate release cycles. Check [schema
compatibility](docs/PYTHON.md#schema-compatibility) before validating an
app-saved session with the Python package.

## Issues

Use GitHub issues for documentation, Python package use, metadata import, and
agent workflow reports.
