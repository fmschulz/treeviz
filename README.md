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

## Documentation

The documentation is organized as a small wiki:

- [Wiki home](docs/index.md)
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
    {
        "id": "A",
        "group": "alpha",
        "value": 1.2,
        "node_diameter": 10,
        "node_color": "#5eead4",
        "branch_width": 2.6,
        "branch_color": "#5eead4",
    },
    {
        "id": "B",
        "group": "alpha",
        "value": 0.8,
        "node_diameter": 9,
        "node_color": "#67e8f9",
        "branch_width": 2.3,
        "branch_color": "#67e8f9",
    },
    {
        "id": "C",
        "group": "beta",
        "value": 2.1,
        "node_diameter": 9,
        "node_color": "#fb923c",
        "branch_width": 2.0,
        "branch_color": "#fb923c",
    },
    {
        "id": "D",
        "group": "beta",
        "value": 1.6,
        "node_diameter": 8,
        "node_color": "#fdba74",
        "branch_width": 1.7,
        "branch_color": "#fdba74",
    },
]
tracks = [
    {"kind": "color_strip", "column_key": "group", "title": "Group"},
    {"kind": "gradient", "column_key": "value", "title": "Value"},
]
view = {
    "nodeCircleDiameterAttribute": "node_diameter",
    "nodeCircleColorAttribute": "node_color",
    "branchWidthAttribute": "branch_width",
    "branchColorAttribute": "branch_color",
    "prettyTerminalBranches": True,
}

session = build_session(tree, metadata=metadata, tracks=tracks, row_key_column="id", view=view)
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
