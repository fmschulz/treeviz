# Use TreeViz From Python

`treeviz-phylo` builds TreeViz-native `.treeviz.json` sessions from Python
scripts and notebooks. It handles tree input, metadata binding, schema
validation, notebook iframe views, basic tree inspection, and static export
through an external renderer command.

The package does not vendor the TreeViz browser app or frontend source. It
ships Python helpers and the TreeViz session schema.

!!! note "Published package compatibility"
    The examples on this page target `treeviz-phylo` 0.3.1, the current PyPI
    release. Its bundled session schema matches the hosted app, so view fields
    such as `conditionalStyleRules` and `branchColorAttribute` validate in
    Python. Browser-side styling is documented in [Tree styling](STYLING.md)
    and [Browser API](API.md).

## Install

```bash
pip install treeviz-phylo
```

Notebook extra:

```bash
pip install "treeviz-phylo[notebook]"
```

Import name:

```python
import treeviz
```

## Minimal Session

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

Open the saved `.treeviz.json` in the browser, or display `view` in a notebook.

## Notebook Use

```python
from IPython.display import display
from treeviz import view_tree

view = view_tree(
    "(A,B,(C,D));",
    metadata=metadata,
    tracks=tracks,
    row_key_column="id",
    open_browser=False,
)
display(view)
```

The session travels in the iframe URL fragment (gzip + base64). Sessions up to
256 KB encoded, roughly 1,500 tips with a few tracks, display inline. Larger
sessions are too large for inline display; save them as `.treeviz.json` and
open the file in the browser.

```python
if view.fragment is None:
    save_session(view.session, "large-session.treeviz.json")
```

## Tree Inputs

`build_session(...)`, `view_tree(...)`, and `render_tree(...)` accept:

- Newick strings;
- Newick or Nexus file paths;
- supported tree objects with Newick export methods;
- Biopython tree objects when Biopython is installed.

Passing a list of trees to `build_session(...)` returns a list of independent
session dictionaries.

## Metadata Inputs

Metadata can be:

- a list or iterable of row dictionaries;
- a pandas `DataFrame`;
- a CSV or TSV file path;
- `None`.

Each row should describe one leaf. One column should match the tree leaf
labels exactly. Pass that column as `row_key_column`.

```python
metadata = [
    {"sample_id": "A", "lineage": "alpha", "load": 1.2, "detected": True},
    {"sample_id": "B", "lineage": "alpha", "load": 0.8, "detected": False},
]

session = build_session("(A,B);", metadata=metadata, row_key_column="sample_id")
```

If `row_key_column` is omitted, the package chooses the metadata column with
the most exact leaf-name matches.

## Track Definitions

Tracks map metadata columns to visual encodings.

| Kind | Required key | Typical use |
| --- | --- | --- |
| `color_strip` | `column_key` | categorical group bands |
| `gradient` | `column_key` | continuous values |
| `heatmap` | `column_keys` | multiple continuous columns |
| `bar` | `column_key` | continuous bar tracks |
| `text` | `column_key` | labels from metadata |
| `binary_dots` | `column_key` | boolean presence/absence symbols |

Example:

```python
tracks = [
    {"kind": "color_strip", "column_key": "lineage", "title": "Lineage"},
    {"kind": "gradient", "column_key": "load", "title": "Load", "palette": "viridis"},
    {"kind": "heatmap", "column_keys": ["score_a", "score_b"], "title": "Scores"},
    {"kind": "bar", "column_key": "day", "title": "Collection day", "show_axis": True},
    {"kind": "binary_dots", "column_key": "detected", "title": "Detected", "shape": "circle"},
    {"kind": "text", "column_key": "note", "title": "Note"},
]
```

Underscores and hyphens are both accepted in track kinds:
`color_strip` and `color-strip` are equivalent.

## View Settings

Pass a `view` dictionary to set layout defaults:

```python
view = {
    "layout": "rectangular",
    "showSupport": True,
    "branchScale": 0.8,
    "leafSpacing": 0.9,
    "metadataGap": 0,
    "labelFontSize": 11,
    "internalNodeMarkerAttribute": "support",
    "internalNodeMarkerEncoding": "shade",
}

session = build_session(tree, metadata=metadata, tracks=tracks, view=view)
```

The browser can further adjust and save view settings.

### Newer Browser Styling

The hosted app can map metadata to exact node circles and branch width/color,
apply conditional rules, draw compact symbol or wedge lanes, and style terminal
branches. `treeviz-phylo` 0.3.1 bundles the same session schema, so these view
fields validate in Python; pass them through the `view` argument or apply them
later through `window.__treeviz`. Metadata branch colours extend to the MRCA
stem of each same-coloured clade (see [Tree styling](STYLING.md)).

## Tree Inspection

```python
from treeviz import binding_diagnostics, leaf_names, tree_stats

leaf_names(session)
tree_stats(session)
binding_diagnostics(session)
```

`binding_diagnostics(session)` reports unmatched leaves, unmatched rows, and
duplicate row keys.

## Static Export

`render_tree(...)` writes a temporary `.treeviz.json` session and calls a
compatible external renderer command. It supports `svg`, `png`, and `pdf`.
Neither the PyPI package nor this public repository installs that renderer.

```python
from treeviz import render_tree

render_tree(
    "(A,B,(C,D));",
    metadata=metadata,
    tracks=tracks,
    format="pdf",
    output="example.pdf",
    command=["/path/to/treeviz-renderer"],
    width=1400,
    height=700,
    auto_crop=True,
    crop_padding=24,
    metrics="example.metrics.json",
)
```

If no renderer command is available, use `view_session(...)`,
`view_tree(...)`, or `session_url(...)` and open the session in the hosted
browser app.

## Public API

| Function | Purpose |
| --- | --- |
| `build_session(tree, metadata=None, tracks=None, view=None, name=None, row_key_column=None)` | Build one session dictionary, or a list of sessions when `tree` is a list. |
| `validate_session(session, schema_path=None)` | Validate a session against the packaged JSON schema. |
| `save_session(session, path)` | Write a `.treeviz.json` session and return the output path. |
| `load_session(path, validate=True, schema_path=None)` | Read a saved session; validation is enabled by default. |
| `view_tree(tree, metadata=None, tracks=None, view=None, open_browser=True, app_url=..., name=None, row_key_column=None)` | Build a session and return a notebook/browser view object. |
| `view_session(session, open_browser=True, app_url=...)` | Return a notebook/browser view for an existing session. |
| `session_url(session, app_url=...)` | Return the hosted TreeViz URL for a session. |
| `leaf_names(tree_or_session)` | Return terminal leaf labels. |
| `tree_stats(tree_or_session)` | Return topology and branch-length summary statistics. |
| `binding_diagnostics(session)` | Return metadata binding diagnostics. |
| `render_tree(tree, metadata=None, tracks=None, view=None, format="svg", output=None, command=None, width=None, height=None, auto_crop=False, crop_padding=None, metrics=None, cwd=None)` | Render SVG, PNG, or PDF through an external renderer command. |
| `TreeVizSession(session, app_url=...)` | Notebook-friendly view object with `.url`, `.fragment`, and `._repr_html_()`. |

## Runnable Example Script

This repository includes a public script that imports the package, builds 30
and 100 leaf examples, validates metadata binding, and writes sessions:

```bash
python examples/plot_treeviz_examples.py --out treeviz-example-output
```

See [Examples](EXAMPLES.md) for static rendering options.
