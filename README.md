# TreeViz

TreeViz is a browser-based viewer for phylogenetic trees, metadata tracks, and
publication figures. It reads Newick, Nexus, TSV/CSV metadata, and
`.treeviz.json` session files.

The live app is available at:

```text
https://treeviz.newlineages.com/
```

This repository contains the public documentation, examples, issue tracker, and
agent skill for TreeViz. It does not contain the browser app source code or a
vendored browser build.

Current compatibility:

- The hosted browser app reports version 0.5.0 through
  [`version.json`](https://treeviz.newlineages.com/version.json). The browser
  API docs and hosted agent skill target that deployment.
- The Python examples target the published
  [`treeviz-phylo` 0.3.1 package](https://pypi.org/project/treeviz-phylo/).
  It writes schema-1 sessions; the hosted app migrates them on load, so the
  examples keep working. One change to know: `layout: "radial"` in a 0.3.1
  session opens as `circular` with straight connectors, which is what the
  0.3.1 app drew under that name. The 0.5.0 `radial` is the unrooted
  equal-daylight layout.

## Documentation

The documentation is organized as a small site:

- [Documentation home](docs/index.md)
- [Getting started](docs/GETTING_STARTED.md)
- [Browser usage](docs/BROWSER.md)
- [Python package](docs/PYTHON.md)
- [Metadata](docs/METADATA.md)
- [Tree styling](docs/STYLING.md)
- [Exports](docs/EXPORTS.md)
- [Browser API](docs/API.md)
- [Agent automation](docs/AGENTS.md)
- [Examples](docs/EXAMPLES.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

The same Markdown pages can be served with MkDocs Material:

```bash
pip install -r requirements-docs.txt
mkdocs serve
```

## Python Package

The PyPI distribution is `treeviz-phylo`; the Python import name is `treeviz`.

```bash
pip install treeviz-phylo
```

Minimal use:

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
view = view_session(session, open_browser=False)
view.url
```

See [Use TreeViz From Python](docs/PYTHON.md) for notebooks, metadata, track
configuration, tree inspection, and static export options.

## Agent Skill

The public skill is in [.agents/skills/treeviz-agent/SKILL.md](.agents/skills/treeviz-agent/SKILL.md).
It is designed for Claude Code, Codex, and other coding agents that need to
open TreeViz, import data, configure tracks, tune layouts, and export figures
through the hosted browser API.

Hosted agent endpoints:

```text
https://treeviz.newlineages.com/?api=1
https://treeviz.newlineages.com/?mode=headless&api=1
```

## Issues

Use GitHub issues in this repository for documentation, Python package usage,
metadata import questions, and agent workflow reports.
