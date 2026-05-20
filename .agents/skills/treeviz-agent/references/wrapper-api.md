# Python Package And Notebook Workflows

Use this reference when an agent needs TreeViz from Python, Jupyter, or a
programmatic pipeline.

## Install

```bash
pip install treeviz-phylo
```

Notebook support:

```bash
pip install "treeviz-phylo[notebook]"
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
    leaf_names,
    save_session,
    tree_stats,
    validate_session,
    view_session,
)

metadata = [
    {
        "id": "A",
        "group": "alpha",
        "value": 1.2,
        "present": True,
        "node_diameter": 11,
        "node_color": "#5eead4",
        "branch_width": 2.8,
        "branch_color": "#5eead4",
    },
    {
        "id": "B",
        "group": "alpha",
        "value": 0.8,
        "present": False,
        "node_diameter": 9,
        "node_color": "#67e8f9",
        "branch_width": 2.2,
        "branch_color": "#67e8f9",
    },
    {
        "id": "C",
        "group": "beta",
        "value": 2.1,
        "present": True,
        "node_diameter": 10,
        "node_color": "#fb923c",
        "branch_width": 2.4,
        "branch_color": "#fb923c",
    },
    {
        "id": "D",
        "group": "beta",
        "value": 1.6,
        "present": False,
        "node_diameter": 8,
        "node_color": "#fdba74",
        "branch_width": 1.8,
        "branch_color": "#fdba74",
    },
]
tracks = [
    {"kind": "color_strip", "column_key": "group", "title": "Group"},
    {"kind": "gradient", "column_key": "value", "title": "Value"},
    {"kind": "binary_dots", "column_key": "present", "title": "Present"},
]
view = {
    "nodeCircleDiameterAttribute": "node_diameter",
    "nodeCircleColorAttribute": "node_color",
    "branchWidthAttribute": "branch_width",
    "branchColorAttribute": "branch_color",
    "prettyTerminalBranches": True,
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

print(leaf_names(session))
print(tree_stats(session))
print(binding_diagnostics(session))
```

## Notebook Display

```python
from IPython.display import display
from treeviz import view_session

view = view_session(session, open_browser=False)
display(view)
```

Small sessions are displayed as an iframe backed by the hosted TreeViz app.
Large sessions should be saved as `.treeviz.json` and opened in the browser.

## Static Export

`render_tree(...)` calls an external renderer command. Use it only when the
environment provides such a command.

```python
from treeviz import render_tree

render_tree(
    "(A,B,(C,D));",
    metadata=metadata,
    tracks=tracks,
    format="png",
    output="example.png",
    command=["treeviz", "render"],
    auto_crop=True,
    crop_padding=24,
)
```

When no renderer command is available, generate `.treeviz.json` and hosted URLs
instead.

## Public Functions

- `build_session`
- `validate_session`
- `save_session`
- `load_session`
- `view_tree`
- `view_session`
- `session_url`
- `leaf_names`
- `tree_stats`
- `binding_diagnostics`
- `render_tree`
- `TreeVizSession`

## View Styling

Pass saved-session view keys through the `view` dictionary. Useful keys for
data-defined styling are:

- `nodeCircleDiameterAttribute`
- `nodeCircleColorAttribute`
- `branchWidthAttribute`
- `branchColorAttribute`
- `prettyTerminalBranches`

The attribute names refer to metadata columns for terminal leaves. Internal
nodes can use the same names when those values are present in tree node
metadata parsed by the browser.
