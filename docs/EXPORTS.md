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

**Include tracks (images)** lists the visible metadata tracks. Clear a track's
checkbox to leave it out of SVG, PNG, and PDF exports. The session is not
changed.

SVG export follows the on-screen rule for zoom: above zoom 1 text, strokes and
node marks are scaled so the file matches what the screen shows; at zoom 1 and
below the SVG is the unzoomed figure. The in-figure legend, including
hand-written `legends`, is part of the export when it is displayed.

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

`export.leaf-names` writes one name per line for `txt`. For `csv` and `tsv`
it writes a `leaf_name` header row, and `includeMetadata: true` adds the
binding's `row_key` and `confidence` columns. The panel exports the whole
tree; **Export leaf names…** in a clade's context menu exports that clade.

Newick, Nexus, leaf-name, and metadata exports do not preserve the TreeViz
visual state. Use `.treeviz.json` when visual state matters.

CSV and TSV leaf-name exports and the metadata TSV export guard against
spreadsheet formulas. A cell that begins with `=`, `+`, `-` or `@` gets a leading apostrophe, so
spreadsheet apps display it literally. Leaf-name exports also guard a leading
tab or carriage return; the metadata TSV replaces tabs and line breaks inside
cells with spaces. Numeric metadata values are written unchanged. TXT leaf-name
exports are not guarded.

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

`auto_crop=True` trims exported SVG, PNG, and PDF artifacts to the visible
content. The metrics JSON records content bounds, crop bounds, whitespace
margins, fill ratios, and crop warnings.
