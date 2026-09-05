# Exports

TreeViz separates complete session exports from figure and data exports.

## Session JSON

Use `.treeviz.json` when the output must preserve the full visualization:

- tree topology and branch lengths;
- metadata table and leaf binding;
- tracks and track order;
- view settings, layout, panel positions, and saved views;
- clade styles, selections, and annotations.

Session JSON is the recommended exchange format between the browser, Python
scripts, notebooks, and agents.

## Figure Formats

Use SVG, PNG, or PDF for figures.

- SVG is best for vector editing and publication layout.
- PNG is best for quick review, web display, and screenshots.
- PDF is best when a downstream workflow expects page-based output.

SVG export follows the on-screen rule for zoom: above zoom 1 text, strokes and
node marks are scaled so the file matches what the screen shows; at zoom 1 and
below the SVG is the unzoomed figure. The in-figure legend, including
hand-written `legends`, is part of the export when it is displayed.

Inside the SVG one `<g data-tv-id="zoom-group">` carries the camera transform
and holds a `<g data-tv-layer="…">` group per draw layer. A collapsed wedge
outline in the radial layout lies inside the wedge fill. The path is stroked at
twice the configured width and clipped to its own shape through a `<clipPath>`
minted for that wedge, so the half of the stroke that would fall outside is
cut away.

For automated rendering, inspect the output after the final layout change.
Whitespace, clipped labels, or unreadable metadata tracks should be fixed in
the layout before the figure is considered final.

## Data Formats

Use Newick or Nexus exports when downstream tools only need the tree. Use
metadata TSV export when downstream tools need the current metadata table.

Newick, Nexus, and metadata exports do not preserve the full TreeViz visual
state. Use `.treeviz.json` when visual state matters.

Cells in CSV and TSV exports (leaf names and metadata values) that begin with
`=`, `+`, `-`, or `@` are prefixed with an apostrophe so spreadsheet apps
display them literally instead of running them as formulas.

## Python Static Export

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
