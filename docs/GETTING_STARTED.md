# Getting Started

TreeViz can be used directly in the browser, from Python, or through the
browser API for agent-driven workflows.

## Browser

Open:

```text
https://treeviz.newlineages.com/
```

Load a Newick or Nexus tree, then add optional TSV/CSV metadata. Save
`.treeviz.json` when you want to preserve tree edits, metadata bindings,
tracks, view settings, and saved views.

## Python

Install the package:

```bash
pip install treeviz-phylo
```

Create and validate a session:

```python
from treeviz import build_session, save_session, validate_session

session = build_session("(A,B,(C,D));")
validate_session(session)
save_session(session, "example.treeviz.json")
```

Open the saved file in the browser, or use `view_session(...)` in a notebook.
See [Python](PYTHON.md) for metadata and notebook examples.

Tree styling can also be saved in the session. Use [Tree styling](STYLING.md)
for data-defined node circles, branch width/color, and the pretty terminal
branch checkbox.

## Agent Automation

Open the hosted app with the public API enabled:

```text
https://treeviz.newlineages.com/?api=1
```

For render-only browser automation:

```text
https://treeviz.newlineages.com/?mode=headless&api=1
```

Agents should call `window.__treeviz.execute(...)` and related API methods
instead of driving the interface through mouse gestures. See
[Agent automation](AGENTS.md) and [Browser API](API.md).

## Basic Inputs

- Tree: Newick or Nexus.
- Metadata: TSV or CSV with one header row and one row per leaf.
- Session: `.treeviz.json` for a complete saved visualization.

## Basic Outputs

- `.treeviz.json`: complete session.
- SVG, PNG, PDF: figures.
- Newick, Nexus, TSV: downstream data exchange.
