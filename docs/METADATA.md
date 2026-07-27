# Metadata

TreeViz metadata is a TSV or CSV table that attaches values to tree leaves.
Those values can drive color strips, gradients, heatmaps, bars, text tracks,
binary dots, branch coloring, clade resolution, and legends.
The hosted browser can also map metadata columns to exact terminal-node circles
and terminal-branch styles.

## Table Shape

Use one header row and one row per leaf.

```tsv
leaf_id	clade	habitat	abundance	present	note
A	Alpha	soil	0.42	yes	reference
B	Alpha	water	1.10	no	candidate
C	Beta	soil	0.08	yes	candidate
```

One column must identify the tree leaf. In the example above, `leaf_id` should
match the leaf labels in the tree.

## Row-Key Column

The row-key column is the metadata column used to bind rows to tree leaves.
Pass it explicitly when you can.

Python:

```python
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

Row-key inference depends on the interface. In Python, omitting
`row_key_column` makes the builder choose the metadata column with the most
exact leaf-name matches. In the browser API, call
`planMetadataImport(source, format, prompt)` first, then pass
`suggestedBinding.rowKeyColumn` to `session.import-metadata`. Explicit row keys
keep workflows reproducible.

## Matching Rules

TreeViz tries exact matches first. During browser import, the metadata planner
can suggest normalization when it improves binding:

- trim leading and trailing whitespace;
- ignore case;
- strip underscores;
- strip common quoted-label decorations.

Unmatched leaves are tree leaves without metadata rows. Unmatched rows are
metadata rows that do not bind to any tree leaf.

## Duplicates And Missing Keys

Row keys should be unique. Duplicate row keys are warnings in the browser
import review, and the last row wins.

Rows with blank row keys cannot be bound. The browser skips them and reports a
warning. In Python, a missing or blank row key raises a `ValueError` so invalid
sessions fail early.

## Values And Types

Cells may contain strings, numbers, booleans, or blanks. Blank cells are
treated as missing values.

TreeViz infers column types:

| Column type | Typical values | Typical tracks |
| --- | --- | --- |
| `continuous` | `0.42`, `1.10`, `3` | gradient, heatmap, bar |
| `binary` | `yes/no`, `true/false`, `1/0`, `present/absent` | binary dots |
| `categorical` | `Alpha`, `Beta`, `soil`, `water` | color strip |
| `text` | labels, notes, long identifiers | text |

## Track Definitions In Python

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

## Style Columns

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

Terminal leaves use tree node metadata first and then the bound metadata row.
Internal nodes only use tree node metadata. Branch style values are keyed by
the child node, so a row for `A1` styles the branch entering `A1`.

See [Tree styling](STYLING.md) for current browser examples.

## File Formats

- `.tsv` and `.tab`: simple tab-separated metadata. Tabs and newlines always
  separate cells and rows.
- `.csv`: CSV with quoted fields.
- `.gz`: accepted by the browser when the filename ends in `.gz`.

Use CSV when fields need quoting, commas, or embedded newlines.

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
