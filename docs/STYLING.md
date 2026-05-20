# Styling Trees

TreeViz can style tree geometry from metadata, tree node annotations, manual
clade edits, or view-wide switches. This page covers node circles, branch
widths, branch colors, and the pretty terminal branch option.

## What Can Be Styled

TreeViz supports these tree-level visual channels:

| Channel | Data type | Applies to |
| --- | --- | --- |
| Node circle diameter | numeric pixels | internal nodes and terminal leaves |
| Node circle color | CSS color string | internal nodes and terminal leaves |
| Branch width | numeric pixels | branch entering a node |
| Branch color | CSS color string | branch entering a node |
| Pretty terminal branches | boolean view option | branches entering terminal leaves |

Branch style values are keyed by the child node: a row or tree annotation for
leaf `A` styles the branch leading into `A`. The root has no incoming branch.

## Browser Controls

The browser Controls panel includes **Exact styling** selectors for node-circle
diameter, node-circle color, branch width, and branch color attributes. These
selectors use columns or tree node metadata already present in the loaded
session.

The same Controls panel includes **Pretty terminal branches**. Enable it to
thicken and round only the branch stubs leading into terminal leaves. The option
works in rectangular, circular, and radial layouts, and it keeps the branch's
current color and mapped width.

For manual edits, right-click a clade and choose **Style clade** to set branch
color, line width, line dash pattern, label color, label style, label font size,
clade annotation, and clade underlay. Select a single leaf or internal node and
open the **Inspector** to directly edit that node's branch color/width and
circle diameter/color.

This is a view setting. It is saved in `.treeviz.json` as:

```json
{
  "view": {
    "prettyTerminalBranches": true
  }
}
```

## TOML Configuration

Use `[view]` fields when building sessions from `treeviz.toml`:

```toml
[view]
node_diameter_attribute = "node_diameter"
node_color_attribute = "node_color"
branch_width_attribute = "branch_width"
branch_color_attribute = "branch_color"
pretty_terminal_branches = true
```

Diameter and width values are interpreted as pixels. Color values should be CSS
color strings such as `#14b8a6` or `rgba(20, 184, 166, 0.8)`.

## Metadata Columns

For terminal leaves, style values can come from bound metadata rows:

```tsv
taxon	group	node_diameter	node_color	branch_width	branch_color
A1	turquoise	11	#5eead4	2.6	#5eead4
A2	turquoise	10	#67e8f9	2.3	#67e8f9
C3	warm	11	#fb923c	2.0	#fb923c
```

This is useful for a gradient from an ancestral clade toward its leaves: put
related colors and decreasing branch widths on the descendant terminal rows,
then enable `pretty_terminal_branches`.

## Tree Node Metadata

Internal nodes do not have metadata table rows. To style internal split circles
or internal branch segments, put values in Newick or Nexus node comments:

```text
((A1:0.1,A2:0.1)[&node_diameter=12,node_color=#14b8a6,branch_width=4,branch_color=#14b8a6]:0.2,C:0.3);
```

For leaves, TreeViz reads tree node metadata first and then falls back to the
bound metadata row. For internal nodes, only tree node metadata is used.

## Ancestral-To-Tip Gradient Example

Use tree node comments for the ancestral split and metadata rows for the
terminal leaves. This example makes one descendant group turquoise with a
broader internal branch that narrows toward the tips, and one terminal path
warm red/orange:

```text
((A1[&node_diameter=10,node_color=#2dd4bf,branch_width=2.8,branch_color=#2dd4bf]:0.08,A2[&node_diameter=9,node_color=#5eead4,branch_width=2.1,branch_color=#5eead4]:0.09)[&node_diameter=13,node_color=#0f766e,branch_width=5,branch_color=#0f766e]:0.20,(B1[&node_diameter=11,node_color=#b91c1c,branch_width=3.6,branch_color=#b91c1c]:0.07,B2[&node_diameter=8,node_color=#fdba74,branch_width=1.8,branch_color=#fdba74]:0.10)[&node_diameter=12,node_color=#ea580c,branch_width=4,branch_color=#ea580c]:0.16,Other:0.30);
```

The same terminal values can also live in metadata:

```tsv
taxon	node_diameter	node_color	branch_width	branch_color
A1	10	#2dd4bf	2.8	#2dd4bf
A2	9	#5eead4	2.1	#5eead4
B1	11	#b91c1c	3.6	#b91c1c
B2	8	#fdba74	1.8	#fdba74
```

Then select the columns with `view.set-tree-style-attributes` or the matching
Python `view` dictionary, and enable `prettyTerminalBranches` when the terminal
branch stubs should be rounded.

## Browser API

Exact style attributes are set with `view.set-tree-style-attributes`:

```js
await api.execute('view.set-tree-style-attributes', {
  nodeDiameterAttribute: 'node_diameter',
  nodeColorAttribute: 'node_color',
  branchWidthAttribute: 'branch_width',
  branchColorAttribute: 'branch_color'
})
```

Pretty terminal branches can be switched independently:

```js
await api.execute('view.set-pretty-terminal-branches', { enabled: true })
```

Pass `null` for an attribute to clear only that mapping:

```js
await api.execute('view.set-tree-style-attributes', {
  nodeColorAttribute: null,
  branchColorAttribute: null
})
```

`view.set-branch-colour-attribute` remains available for numeric branch-color
gradients. Exact branch colors from `view.set-tree-style-attributes` take
precedence when both are active.

## Python Package

The Python package accepts the same saved-session view keys through the `view`
dictionary:

```python
from treeviz import build_session, validate_session

metadata = [
    {
        "id": "A",
        "node_diameter": 10,
        "node_color": "#5eead4",
        "branch_width": 2.6,
        "branch_color": "#5eead4",
    },
    {
        "id": "B",
        "node_diameter": 8,
        "node_color": "#fb923c",
        "branch_width": 1.8,
        "branch_color": "#fb923c",
    },
]

view = {
    "nodeCircleDiameterAttribute": "node_diameter",
    "nodeCircleColorAttribute": "node_color",
    "branchWidthAttribute": "branch_width",
    "branchColorAttribute": "branch_color",
    "prettyTerminalBranches": True,
}

session = build_session("(A:0.2,B:0.2);", metadata=metadata, row_key_column="id", view=view)
validate_session(session)
```

The package validates against the same session schema used by the browser. That
means new view fields such as `prettyTerminalBranches` should be preserved in
saved sessions and notebook views.

## Practical Notes

- Use metadata table columns for terminal leaves and tree node comments for
  internal nodes.
- Keep widths modest when labels or metadata tracks are dense; very large
  terminal strokes can cover nearby tips.
- Pretty terminal branches are view-wide. Use branch color and branch width
  attributes to decide which terminal paths are visually emphasized.
- Save a `.treeviz.json` session after styling so the exact mappings and the
  checkbox state can be reopened later.
