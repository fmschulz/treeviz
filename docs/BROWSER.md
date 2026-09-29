# Browser usage

TreeViz runs as a static browser app.

## Open

- [https://treeviz.newlineages.com/](https://treeviz.newlineages.com/) opens
  the app.
- [https://treeviz.newlineages.com/?api=1](https://treeviz.newlineages.com/?api=1)
  also exposes the `window.__treeviz` browser API.
- [https://treeviz.newlineages.com/?mode=headless&api=1](https://treeviz.newlineages.com/?mode=headless&api=1)
  is a render-only mode for automation. It exposes the same API.

## Load data

TreeViz accepts:

- Newick (including IQ-TREE `.contree`) and Nexus tree files;
- `.treeviz.json` sessions;
- TSV/CSV metadata tables with one header row;
- gzipped (`.gz`) copies of any of these files.

Drop files onto the page or use the file picker. Load the tree first, then
the metadata, and choose the row-key column that matches metadata rows to tree
leaves.

## Configure the view

Metadata tracks encode table values next to leaves: color strips for
categories, gradients and heatmaps for continuous values, bars for numeric
comparisons, text tracks for labels, binary dots for presence and absence.
The **Tracks** panel lists each track by title. Expand a track to edit its
columns, palette, width, and other settings; the first track is open when the
panel appears. The same panel adds and removes tracks.

The stage toolbar switches layout, turns **Auto size** on or off, fits the
tree, searches taxa and clades, shows or hides branch lengths, and opens the
panels. It also sets tip alignment in the rectangular layout, switches arc or
straight connectors in the circular layout, and saves and restores named views. The **Controls** panel starts
with quick actions for label and metadata-track visibility, followed by four
groups:

- **Layout**: zoom, automatic collapse threshold, and scale-bar visibility.
  Rectangular and circular layouts add **Collapsed clade spacing**
  (**Proportional** or **Compact**). Circular layout also provides opening,
  rotation, imported node angles, **Auto-fit to labels**, **Tip-to-track
  guides**, and opening/interior fill controls. **Node angles (degrees)** lists
  numeric attributes stored directly on tree nodes; **Automatic** uses
  TreeViz's computed angles. Radial layout provides **Node X coordinate** and
  **Node Y coordinate**, which read display positions from node attributes.
- **Labels**: label font and size, support labels, and **Auto-cull overlaps**.
  Auto-cull overlaps (TOML
  `allow_label_overlap = false`) drops a label that would land on one already
  drawn; zooming in brings it back.
- **Branches & nodes**: **Tree width**, **Branch stroke width**, **Branch
  spacing**, **Pretty terminal branches**, **Show node circles**, **Colour
  by**, **Exact styling**, and **Split circles**. Branch spacing scales row pitch in the rectangular
  layout. In the radial layout it shapes the angular split so crowded clades
  can receive more room. **Colour by** maps a numeric metadata column onto a
  scale or applies exact colors stored in node attributes. **Exact styling**
  maps node-circle diameter or color and branch width or color from data
  attributes. **Split circles** draws internal-node markers from support
  values or a numeric node attribute, and appears when internal nodes other than
  the root carry one. Wedge outlines follow the
  branch color.
- **Metadata**: adjust metadata-track widths, row height, and gap. Add, remove,
  and edit the tracks themselves in **Tracks**.

Collapsed-wedge controls appear under **Branches & nodes** in the radial
layout. They include shape, fill source and opacity, gap, minimum body, overlap
policy, data-driven size, background outline, and label placement.

Any label can be dragged: press on the text and move it. The offset is stored
on that clade, so it survives saving and appears in exports.

For one-off edits, select a leaf or internal node and use the Inspector's
branch, circle, and label controls. Saved views keep more than one arrangement
of the same session. Every option is listed in [Tree styling](STYLING.md).

The **Legend** panel lists the legends derived from tracks, markers, node marks
and connections, then any hand-written legends stored on the session
(`legends`, from `[[legend]]` tables in a TOML config). **Display in figure**
places a section on the canvas; the in-figure legend is part of SVG, PNG, and
PDF exports. Session JSON can also supply a continuous size/color legend. Its
standalone figure section is frameless, with the title above the ramp; the side
panel keeps its normal container.

## Navigate

Scroll to zoom and drag to pan. **Fit** (`F`) fits the whole tree into the
viewport; `0` resets zoom and pan. Above zoom 1 the topology grows while
labels, branch strokes, node circles and leaf markers keep their screen size,
so zooming in opens space between labels and brings back the labels the
overlap culler dropped at fit. The culler re-runs about 150 ms after the
camera stops moving. Below zoom 1 everything shrinks with the tree. The camera
stays where you put it when you open a panel or edit the document; the view
refits only when a session loads or the layout changes. In the rectangular
layout the fitted view includes collapsed wedge tips and their labels.

Hovering a leaf, an internal node or a collapsed wedge shows a tooltip: the
label or name, `N leaves` for a wedge, `Branch length x`, `Support y`, then the
node's attributes under their display names, with a swatch for color values.
Hovering or selecting a collapsed wedge outlines its polygon.

A collapsed clade's label sits past its wedge tip. Two controls under
**Collapsed wedges** set its placement:

- **Label direction**: **Along branch** (the default) reads along the branch
  that enters the clade. **Outward** reads out from the center of the drawing.
  TOML key: `collapsed_wedge_label_orientation` (`"branch"` or `"bearing"`).
- **Wedge labels**: **At wedge tip** (the default) seats every label at its
  tip. **Leader lines** pushes a label that would land on another out along its
  branch and joins it to the wedge with a thin line in the label's color. TOML
  key: `collapsed_wedge_label_declutter` (`false` or `true`).

See [Tree styling](STYLING.md#label-color-direction-and-position).

The search field (**Search taxa and clades…**) matches leaf names, leaf labels
and collapsed-clade labels. A hit inside a collapsed clade lands on that
clade's wedge. **Enter** zooms to the active hit (to at least 2x);
**Shift+Enter** and the arrow keys step through the hits; **Escape** clears
the search.

## Save and export

Use `.treeviz.json` to preserve the full visualization. Use SVG, PNG, or PDF
for figures. Use Newick, Nexus, and metadata TSV exports for downstream data
exchange.

See [Exports](EXPORTS.md) for format guidance.

## Public machine-readable files

The deployed app publishes:

- `https://treeviz.newlineages.com/version.json`
- `https://treeviz.newlineages.com/treeviz-command-schema.json`
- `https://treeviz.newlineages.com/treeviz-session.schema.json`
- `https://treeviz.newlineages.com/examples/manifest.json`

Use the session schema to validate `.treeviz.json` files generated by wrappers
or external pipelines before opening them in TreeViz.
