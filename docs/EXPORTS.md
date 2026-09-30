# Exports

TreeViz separates complete session exports from figure and data exports.

## Session JSON

Use `.treeviz.json` when the output must preserve the full visualization:

- tree topology and branch lengths;
- metadata table and leaf binding;
- tracks and track order;
- view settings, layout, panel positions, and saved views;
- clade styles, selections, and annotations.

Session JSON is the exchange format between the browser, Python scripts,
notebooks, and agents.

## Figure formats

The **Images** section of the **Export** panel writes SVG, PNG, and PDF
figures. Each image export is
cropped to the visible content.

- SVG keeps text, paths, and shapes as editable vectors. **Copy SVG** puts the
  same SVG on the clipboard.
- PNG is a raster image. **PNG options** set the resolution to 72, 150, 300,
  or 600 DPI (default 300) and can make the background transparent.
- PDF keeps the vector figure on a page. **PDF options** set the page to
  **Fit to tree** (default, the page matches the cropped figure), **Letter**,
  or **A4**. Letter and A4 pages take **Portrait** or **Landscape** and center
  the figure on the page.

**Include tracks (images)** lists every visible metadata track. To leave a
track out of SVG, PNG, and PDF exports, clear its checkbox. This setting does
not change the session.

SVG export treats zoom the same way the screen does. Above zoom 1, text,
strokes and node marks are scaled so the file matches the on-screen view. At
zoom 1 and below, the SVG contains the unzoomed figure. When the in-figure
legend is displayed, the export includes it, along with any hand-written
`legends`.

For automated rendering, inspect the output after the final layout change.
Whitespace, clipped labels, or unreadable metadata tracks should be fixed in
the layout before the figure is considered final.

## Data formats

The **Data** section of the **Export** panel runs these commands. Each one
returns `{ content, filename, mimeType }` in `ExecuteResult.value` when called
through `window.__treeviz.execute`.

| Command | Output | Arguments |
| --- | --- | --- |
| `export.newick` | Newick tree | none |
| `export.nexus` | Nexus tree | optional `taxaBlock` |
| `export.leaf-names` | leaf names under one clade as `txt`, `csv`, or `tsv` | `stableKey`, `format`, `includeMetadata` |
| `export.metadata-tsv` | current metadata table as TSV | none |

For `txt`, `export.leaf-names` writes one name per line. For `csv` and `tsv`,
it starts with a `leaf_name` header row, and `includeMetadata: true` adds the
binding's `row_key` and `confidence` columns. The panel exports the whole
tree. To export a single clade, use **Export leaf names…** in that clade's
context menu.

Newick, Nexus, leaf-name, and metadata exports do not preserve the TreeViz
visual state. Use `.treeviz.json` when visual state matters.

The CSV and TSV leaf-name exports and the metadata TSV export protect against
spreadsheet formulas. When a cell begins with `=`, `+`, `-` or `@`, it gets a
leading apostrophe, and spreadsheet apps show it as literal text. Leaf-name
exports also guard a leading tab or carriage return, while the metadata TSV
replaces tabs and line breaks inside cells with spaces. Numeric metadata
values are written as they are. TXT leaf-name exports have no guard.

## Python static export

The Python package can call a compatible external renderer. Neither the PyPI
package nor this public repository installs one.

```python
from treeviz import render_tree

render_tree(
    "(A,B,(C,D));",
    format="svg",
    output="tree.svg",
    command=["/path/to/treeviz-renderer"],
    width=1400,
    height=700,
    auto_crop=True,
    crop_padding=24,
    metrics="tree.metrics.json",
)
```

With `auto_crop=True`, exported SVG, PNG, and PDF artifacts are trimmed to
their visible content. The metrics JSON records the content bounds, crop
bounds, whitespace margins, fill ratios, and any crop warnings.
