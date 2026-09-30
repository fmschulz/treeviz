# Metadata

In TreeViz, metadata is a TSV or CSV table whose values attach to the leaves
of the tree. You can use those values to drive color strips, gradients,
heatmaps, bars, text tracks, binary dots, branch coloring, clade resolution,
and legends. In the hosted browser, metadata columns can also map to exact
terminal-node circles and terminal-branch styles.

## Table shape

Use one header row and one row per leaf.

```tsv
leaf_id	clade	habitat	abundance	present	note
A	Alpha	soil	0.42	yes	reference
B	Alpha	water	1.10	no	candidate
C	Beta	soil	0.08	yes	candidate
```

One column must identify the tree leaf. In the example above, `leaf_id` should
match the leaf labels in the tree.

## Row-key column

The row-key column is the metadata column used to bind rows to tree leaves.
Pass it explicitly where possible.

Python:

```python
from treeviz import build_session

metadata = [
    {"leaf_id": "A", "clade": "Alpha", "habitat": "soil", "abundance": 0.42},
    {"leaf_id": "B", "clade": "Alpha", "habitat": "water", "abundance": 1.10},
    {"leaf_id": "C", "clade": "Beta", "habitat": "soil", "abundance": 0.08},
]

session = build_session(
    "(A,B,C);",
    metadata=metadata,
    row_key_column="leaf_id",
)
```

Browser API:

```js
await api.execute('session.import-metadata', {
  source: metadataText,
  format: 'tsv',
  rowKeyColumn: 'leaf_id'
})
```

How the row key is inferred depends on the interface you use. In Python, leave
out `row_key_column` and the builder picks the metadata column with the most
exact leaf-name matches. In the browser API, first call
`planMetadataImport(source, format, prompt)`, then pass
`suggestedBinding.rowKeyColumn` to `session.import-metadata`. Setting the row
key explicitly keeps a workflow reproducible.

## Matching rules

TreeViz tries exact matches first. During browser import, the metadata planner
can suggest normalization when it improves binding:

- trim leading and trailing whitespace;
- ignore case;
- strip underscores;
- strip common quoted-label decorations.

Unmatched leaves are tree leaves without metadata rows. Unmatched rows are
metadata rows that do not bind to any tree leaf.

## Duplicates and missing keys

Row keys should be unique. Duplicate row keys are warnings in the browser
import review, and the last row wins.

Rows with blank row keys cannot be bound. The browser skips them and reports a
warning. In Python, a missing or blank row key raises a `ValueError` so invalid
sessions fail early.

## Values and types

Cells may contain strings, numbers, booleans, or blanks. Blank cells are
treated as missing values.

TreeViz infers column types:

| Column type | Typical values | Typical tracks |
| --- | --- | --- |
| `continuous` | `0.42`, `1.10`, `3` | gradient, heatmap, bar |
| `binary` | `yes/no`, `true/false`, `1/0`, `present/absent` | binary dots |
| `categorical` | `Alpha`, `Beta`, `soil`, `water` | color strip |
| `text` | labels, notes, long identifiers | text |

## Track definitions in Python

```python
tracks = [
    {"kind": "color_strip", "column_key": "clade", "title": "Clade"},
    {"kind": "gradient", "column_key": "abundance", "title": "Abundance"},
    {"kind": "bar", "column_key": "abundance", "title": "Abundance", "show_axis": True},
    {"kind": "binary_dots", "column_key": "present", "title": "Present", "shape": "circle"},
    {"kind": "text", "column_key": "note", "title": "Note"},
]
```

`color_strip` and `binary_dots` may also be written as `color-strip` and
`binary-dots`. The Python package normalizes underscores to hyphens.

## Style columns

Metadata columns can drive terminal-node circles and terminal-branch styling:

```tsv
taxon	group	node_diameter	node_color	branch_width	branch_color
A1	turquoise	11	#5eead4	2.6	#5eead4
A2	turquoise	10	#67e8f9	2.3	#67e8f9
C3	warm	11	#fb923c	2.0	#fb923c
```

Map those columns through the hosted browser API:

```js
await api.execute('view.set-tree-style-attributes', {
  nodeDiameterAttribute: 'node_diameter',
  nodeColorAttribute: 'node_color',
  branchWidthAttribute: 'branch_width',
  branchColorAttribute: 'branch_color'
})

await api.execute('view.set-pretty-terminal-branches', { enabled: true })
```

Node attributes are key-value pairs stored on the tree nodes themselves, such
as values read from Newick or Nexus comments. They are not the same as the node
metadata table (`session.import-node-metadata`). That table binds TSV rows to
internal nodes and feeds node marks and node search.

For terminal leaves, TreeViz reads node attributes first and then falls back
to the bound metadata row. Internal nodes read node attributes only. Branch
style values are keyed by the child node, so a row for `A1` styles the branch
that enters `A1`.

You can give a node attribute a display name with `[attribute_labels]` in a
TOML config (session `attributeLabels`). The Controls pickers and hover
tooltips then show it as `Name (key)`. For details, see
[Legends and attribute names](STYLING.md#legends-and-attribute-names).

See [Tree styling](STYLING.md) for current browser examples.

## File formats

- `.tsv` and `.tab`: simple tab-separated metadata. Tabs and newlines always
  separate cells and rows.
- `.csv`: CSV with quoted fields.

Use CSV when fields need quoting, commas, or embedded newlines.

Gzipped files (`*.tsv.gz`, `*.tab.gz`, `*.csv.gz`) are decompressed in the
browser.

## Validation

Python:

```python
from treeviz import binding_diagnostics, validate_session

validate_session(session)
binding_diagnostics(session)
```

Browser API:

```js
api.getDiagnostics()
```

Large unmatched counts usually mean the wrong row-key column or normalization
settings were used.
