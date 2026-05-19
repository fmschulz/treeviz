# Metadata FAQ

TreeViz metadata is a TSV or CSV table that attaches values to tree leaves.
Those values can then drive color strips, gradients, heatmaps, bars, text
tracks, binary dots, branch coloring, labels, and clade resolution.

## What does a metadata file look like?

Use one header row and one row per sample, genome, gene, or taxon.

```tsv
leaf_id	phylum	habitat	abundance	present	host
A	Proteobacteria	soil	0.42	yes	mouse
B	Firmicutes	water	1.10	no	human
C	Actinobacteriota	soil	0.08	yes	mouse
```

The first column does not have to be called `leaf_id`, but one column must be
chosen as the row-key column during import.

## What is the row-key column?

The row-key column is the metadata column used to match rows to tree leaves.
By default TreeViz compares row-key values with leaf labels from the Newick or
Nexus tree.

For the example above, a tree containing leaves `A`, `B`, and `C` should import
with `leaf_id` as the row-key column.

## Can the row-key column have duplicates?

It should be unique. Duplicate row keys are accepted, but the last row wins in
the stored metadata table. TreeViz reports duplicate keys as warnings in the
import review.

## What happens to blank row keys?

Rows with a blank value in the row-key column are skipped and reported as
warnings. A row without a key cannot be bound to a leaf.

## How are metadata rows matched to leaves?

TreeViz tries exact matches first. If exact matching fails, it can apply
normalization flags:

- Trim leading and trailing whitespace.
- Ignore case.
- Strip underscores.
- Strip common quoted-label decorations such as `/1`, branch-length suffixes,
  and surrounding single quotes.

The default normalization is trim-only. The import planner can suggest stronger
normalization when it improves binding.

## Can metadata bind to tree annotations instead of leaf labels?

Yes. If the tree leaves carry metadata in Newick/Nexus node comments, TreeViz
can use a leaf metadata field as the leaf identifier source. For example,
leaves with NHX or BEAST-style comments can be matched by a metadata key in
`node.meta` instead of by the visible label.

## Which file formats are supported?

- `.tsv` and `.tab`: tab-separated metadata.
- `.csv`: RFC 4180-style CSV with quoted fields.
- Gzipped files are accepted when the filename ends in `.gz`.

TSV is intentionally simple: tabs and newlines always separate cells and rows.
If a field needs quotes, commas, or embedded newlines, use CSV.

## How are column types inferred?

TreeViz infers a starting type for each column:

- All finite numeric values -> `continuous`.
- Values such as `true`, `false`, `yes`, `no`, `1`, `0`, `present`, `absent`
  -> `binary`.
- Two distinct non-numeric values -> `binary`.
- Up to 32 distinct non-numeric values -> `categorical`.
- More distinct values -> `text`.

Empty cells are ignored during inference and become missing values in the
stored table.

## How should missing values be written?

Leave the cell empty.

```tsv
leaf_id	habitat	abundance
A	soil	0.42
B	water	
C	soil	0.08
```

Missing values are stored as `null`.

## What do unmatched leaves and unmatched rows mean?

- Unmatched leaves are tree leaves that did not find a metadata row.
- Unmatched rows are metadata rows that did not bind to any leaf.

A small number can be acceptable for partial metadata. Large counts usually
mean the wrong row-key column or normalization settings were chosen.

## How do I configure metadata in `treeviz.toml`?

```toml
[metadata]
file = "metadata.tsv"
format = "tsv"
row_key_column = "leaf_id"

[binding]
trim = true
case_insensitive = false
strip_underscores = false
strip_quoted_label_decorations = false

[[track]]
kind = "color-strip"
column = "phylum"

[[track]]
kind = "heatmap"
columns = ["abundance"]

[[track]]
kind = "bar"
column = "abundance"
show_axis = true
show_helper_lines = true
helper_line_style = "dashed"
```

The CLI compiles this into a self-contained `.treeviz.json` session.

## What should I export if I want to preserve metadata tracks?

Use **Export Session (JSON)**. Newick and Nexus exports preserve tree data but
do not preserve metadata tables, bindings, tracks, view settings, or saved
views.
