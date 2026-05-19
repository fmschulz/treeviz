# Use TreeViz From Python

`treeviz-phylo` is the Python package for building TreeViz-native
`.treeviz.json` sessions from scripts and notebooks. It provides helpers for
tree input, metadata binding, validation, notebook iframe views, and static
exports through an external TreeViz renderer.

The package does not vendor the TreeViz browser app, `dist/`, `public/`,
`src/`, `node_modules/`, or other frontend source. Static SVG/PNG/PDF export
uses an installed TreeViz CLI or a source checkout; interactive notebook views
use the hosted app at `https://treeviz.newlineages.com/`.

## Install

After a release is uploaded to PyPI:

```bash
pip install treeviz-phylo
```

For notebooks that import `IPython.display`:

```bash
pip install "treeviz-phylo[notebook]"
```

Development installs from a source checkout are maintained in the private
implementation repository.

Import name:

```python
import treeviz
```

## Minimal Example

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

In a notebook:

```python
from IPython.display import display

display(view)
```

## Runnable Plotting Script

This repository includes a script that imports the package, builds two
example sessions, validates metadata binding, writes `.treeviz.json`, and
renders SVG, PNG, and PDF outputs through the TreeViz CLI:

```bash
python examples/plot_treeviz_examples.py \
  --out /tmp/treeviz-python-plots
```

The same script can be used after a PyPI install. If no local renderer is
available, use `--skip-static` to write sessions and hosted URLs only.

## Metadata Structure

Metadata can be provided as:

- a list or iterable of row dictionaries;
- a pandas `DataFrame`;
- a CSV or TSV file path;
- `None`.

Each metadata row should describe one leaf. One column must identify the tree
leaf label exactly. Pass that column as `row_key_column` whenever possible:

```python
metadata = [
    {"sample_id": "A", "lineage": "alpha", "load": 1.2, "detected": True},
    {"sample_id": "B", "lineage": "alpha", "load": 0.8, "detected": False},
]
session = build_session("(A,B);", metadata=metadata, row_key_column="sample_id")
```

If `row_key_column` is omitted, TreeViz chooses the metadata column with the
most exact leaf-name matches. Use `binding_diagnostics(session)` after building
to check unmatched leaves or rows.

Cell values may be strings, numbers, booleans, `None`, or empty strings. Empty
strings and `None` are treated as missing values. Column types are inferred as
continuous, binary, categorical, or text.

## Tracks

Tracks are dictionaries that map metadata columns to visual encodings. Use
`column_key` for one column and `column_keys` for heatmaps. Underscores in
`kind` are normalized to hyphens, so `color_strip` and `color-strip` are both
accepted.

Supported track kinds:

| Kind | Required columns | Typical use |
| --- | --- | --- |
| `color_strip` | `column_key` | categorical group bands |
| `gradient` | `column_key` | continuous values |
| `heatmap` | `column_keys` | multiple continuous columns |
| `bar` | `column_key` | continuous bar tracks |
| `text` | `column_key` | labels from metadata |
| `binary_dots` | `column_key` | boolean presence/absence |

Example:

```python
tracks = [
    {"kind": "color_strip", "column_key": "lineage", "title": "Lineage"},
    {"kind": "gradient", "column_key": "load", "title": "Load", "palette": "viridis"},
    {"kind": "bar", "column_key": "day", "title": "Collection day", "show_axis": True},
    {"kind": "binary_dots", "column_key": "detected", "title": "Detected"},
]
```

## Static Exports

`render_tree(...)` writes a temporary `.treeviz.json` session and calls a
TreeViz renderer command. It supports `svg`, `png`, and `pdf`.

If you have access to a TreeViz renderer command:

```python
from pathlib import Path
from treeviz import render_tree

render_tree(
    "(A,B,(C,D));",
    metadata=metadata,
    tracks=tracks,
    format="pdf",
    output="example.pdf",
    width=1400,
    height=620,
    auto_crop=True,
    crop_padding=24,
    metrics="example.metrics.json",
    command=["treeviz", "render"],
)
```

`render_tree` defaults to `bun run treeviz render`, which is meant for the
TreeViz implementation checkout. Public package users should provide a renderer
command with `command=[...]` when one is available. If no local renderer is
available, use `view_session(...)` or `session_url(...)` to open sessions in the
hosted browser app.

`auto_crop=True` tightens SVG, PNG, and PDF exports to the visible tree content
after rendering. `crop_padding` is measured in pixels. `metrics` writes a JSON
file with the measured content box, crop box, whitespace margins, fill ratios,
and warnings such as `excess-vertical-whitespace`.

## Public API

`build_session(tree, metadata=None, tracks=None, view=None, name=None, row_key_column=None)`

Build one TreeViz session from a Newick string, Newick/Nexus file path, or a
supported tree object. A list of trees returns a list of sessions.

`validate_session(session, schema_path=None)`

Validate a session against the packaged TreeViz session JSON schema.

`save_session(session, path)`

Write a `.treeviz.json` session and return the output path.

`load_session(path, validate=True, schema_path=None)`

Read a saved session. Validation is enabled by default.

`view_tree(tree, metadata=None, tracks=None, view=None, open_browser=True, app_url=..., name=None, row_key_column=None)`

Build a session and return a `TreeVizSession` view object. Set
`open_browser=False` in notebooks and scripts.

`view_session(session, open_browser=True, app_url=...)`

Return a `TreeVizSession` view object for an existing session.

`session_url(session, app_url=...)`

Return the hosted TreeViz URL for a session. Small sessions are encoded in the
URL fragment; large sessions return the base app URL and should be opened from
a saved `.treeviz.json` file.

`leaf_names(tree_or_session)`

Return terminal leaf labels from a Newick/tree object, TreeViz tree document,
or full TreeViz session.

`tree_stats(tree_or_session)`

Return leaf count, internal-node count, total-node count, max depth, tree
height, rooted/binary flags, and branch-length summary.

`binding_diagnostics(session)`

Return metadata binding diagnostics, including unmatched leaves and unmatched
metadata rows.

`render_tree(tree, metadata=None, tracks=None, view=None, format="svg", output=None, command=None, width=None, height=None, auto_crop=False, crop_padding=None, metrics=None, cwd=None)`

Render SVG, PNG, or PDF through the external TreeViz renderer and return the
output path.

`TreeVizSession(session, app_url=...)`

Notebook-friendly view object. It exposes `.url`, `.fragment`, and
`._repr_html_()` for iframe display.

## Verification

The implementation repository runs package checks before publishing:

```bash
pixi run -e py py-test
pixi run -e py py-example
pixi run -e py py-notebook
pixi run -e py py-build
pixi run -e py py-twine-check
pixi run -e py py-package-check
```
