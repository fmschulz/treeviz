# Python Package And Notebook Workflows

Use this reference for the published Python package, Jupyter, or a Python
pipeline.

## Compatibility

The current PyPI release is `treeviz-phylo` 0.3.1. It builds and validates
TreeViz sessions against the previous session schema; the hosted app (0.5.0)
migrates them on load, and a 0.3.1 `radial` layout opens as `circular` with
straight connectors. The package still validates the current view fields,
so view fields such as `conditionalStyleRules`, `branchColorAttribute`,
`nodeCircleDiameterAttribute`, and `prettyTerminalBranches` validate in Python.
Track dictionaries accept `category_colors`, `display_mode`, `bins`, and
`auto_bins` (or their camelCase forms). Sessions written by the 0.1.0 package
still load; the hosted app migrates them and keeps their branch scale in manual
mode. Call `view.set-branch-scale-mode` with `{ mode: 'auto' }` after load when
such a figure should follow automatic sizing.

## Install

```bash
pip install treeviz-phylo==0.3.1
```

Notebook support:

```bash
pip install "treeviz-phylo[notebook]==0.3.1"
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
    "conditionalStyleRules": [
        {
            "id": "alpha-branches",
            "source": "group",
            "condition": {"kind": "exact", "value": "alpha"},
            "target": "branch-color",
            "value": "#1d4ed8",
        }
    ],
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

The `branch-color` rule paints the alpha tips and, because they form a
monophyletic group, the branches up to and including their MRCA stem. Track
kinds are `color-strip`, `gradient`, `heatmap`, `bar`, `stacked-bar`, `text`,
and `binary-dots`; underscore spellings such as `color_strip` are accepted.

## Notebook Display

```python
from IPython.display import display

display(view_object)
```

The view is an iframe of the hosted app with the session in the URL fragment.
Sessions up to 256 KB encoded (roughly 1,500 tips with a few tracks) display
inline. Larger sessions show a message instead; save them with `save_session`
and open the file in the browser. `view_object.fragment` is `None` in that case.

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
