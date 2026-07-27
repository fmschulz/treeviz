# Python Package And Notebook Workflows

Use this reference for the published Python package, Jupyter, or a Python
pipeline.

## Compatibility Boundary

The current PyPI release is `treeviz-phylo` 0.1.0. It builds and validates
TreeViz sessions, but its bundled schema predates several hosted browser
features. The hosted app migrates 0.1.0 sessions when it loads them. Do not pass
newer browser-only view fields into `validate_session(...)`.

Browser-only fields in the current hosted app include exact node-circle
attribute mappings, exact branch width/color attribute mappings, pretty
terminal branches, conditional style rules, automatic branch-scale mode, node
marks, and tip connections. Build the base session in Python, then apply these
features through `window.__treeviz` or a current browser-authored session.

The 0.1.0 builder also drops `category_colors`, `display_mode`, `bins`, and
`auto_bins` from track dictionaries. Apply `categoryColors`, `displayMode`,
`bins`, or `autoBins` through `track.update` after the hosted app loads the
session.

The hosted migration preserves the legacy branch scale by selecting manual
mode. Call `view.set-branch-scale-mode` with `{ mode: 'auto' }` after load when
the figure should follow current automatic sizing.

## Install

```bash
pip install treeviz-phylo==0.1.0
```

Notebook support:

```bash
pip install "treeviz-phylo[notebook]==0.1.0"
```

Import:

```python
import treeviz
```

## Typical Use

```python
from treeviz import (
    binding_diagnostics,
    build_session,
    save_session,
    validate_session,
    view_session,
)

metadata = [
    {"id": "A", "group": "alpha", "value": 1.2, "present": True},
    {"id": "B", "group": "alpha", "value": 0.8, "present": False},
    {"id": "C", "group": "beta", "value": 2.1, "present": True},
    {"id": "D", "group": "beta", "value": 1.6, "present": False},
]
tracks = [
    {"kind": "color_strip", "column_key": "group", "title": "Group"},
    {"kind": "gradient", "column_key": "value", "title": "Value"},
    {"kind": "binary_dots", "column_key": "present", "title": "Present"},
]
view = {
    "layout": "rectangular",
    "showSupport": True,
    "branchScale": 0.8,
    "leafSpacing": 0.9,
    "metadataGap": 0,
}

session = build_session(
    "(A,B,(C,D));",
    metadata=metadata,
    tracks=tracks,
    view=view,
    row_key_column="id",
)
validate_session(session)
save_session(session, "example.treeviz.json")

print(binding_diagnostics(session))
view_object = view_session(session, open_browser=False)
```

Supported 0.1.0 track kinds are `color-strip`, `gradient`, `heatmap`, `bar`,
`text`, and `binary-dots`. Underscore spellings such as `color_strip` are also
accepted.

## Notebook Display

```python
from IPython.display import display

display(view_object)
```

Small sessions use a hosted TreeViz iframe. Large sessions should be saved as
`.treeviz.json` and opened in the browser.

## Static Export

`render_tree(...)` calls a compatible external renderer. Neither the PyPI
package nor this public repository installs one.

```python
from treeviz import render_tree

render_tree(
    "(A,B,(C,D));",
    metadata=metadata,
    tracks=tracks,
    format="png",
    output="example.png",
    command=["/path/to/treeviz-renderer"],
    auto_crop=True,
    crop_padding=24,
)
```

Without a renderer command, save `.treeviz.json` or use `view_session(...)`.

## Public Functions

| Function | Purpose |
| --- | --- |
| `build_session` | Build one session, or one session per tree in a list. |
| `validate_session` | Validate against the schema bundled with the package. |
| `save_session` | Write `.treeviz.json`. |
| `load_session` | Read and optionally validate a saved session. |
| `view_tree` | Build a tree session and return a notebook/browser view. |
| `view_session` | Return a notebook/browser view for an existing session. |
| `session_url` | Create a hosted TreeViz URL for a session. |
| `leaf_names` | Return terminal labels. |
| `tree_stats` | Return topology and branch-length statistics. |
| `binding_diagnostics` | Report unmatched leaves, rows, and duplicate keys. |
| `render_tree` | Call an external renderer for SVG, PNG, or PDF. |
| `TreeVizSession` | Notebook view object with URL and HTML display methods. |

Always run `validate_session(session)` and inspect
`binding_diagnostics(session)` before handing off a Python-generated session.
