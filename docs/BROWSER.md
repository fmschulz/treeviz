# Browser Usage

TreeViz runs as a static browser app.

## Open

```text
https://treeviz.newlineages.com/
```

API-enabled mode:

```text
https://treeviz.newlineages.com/?api=1
```

Headless automation mode:

```text
https://treeviz.newlineages.com/?mode=headless&api=1
```

## Load Data

TreeViz accepts:

- Newick and Nexus tree files;
- `.treeviz.json` sessions;
- TSV/CSV metadata tables with one header row.

Drop files onto the page or use the file picker. Load the tree first, then
the metadata, and choose the row-key column that matches metadata rows to tree
leaves.

## Configure The View

Metadata tracks encode table values next to leaves: colour strips for
categories, gradients and heatmaps for continuous values, bars for numeric
comparisons, text tracks for labels, binary dots for presence and absence.
The **Tracks** panel lists each track by title. Expand a track to edit its
columns, palette, width, and other settings; the first track is open when the
panel appears. The same panel adds and removes tracks.

The stage toolbar switches layout, shows or hides branch lengths, sets tip
alignment, fits the tree, and opens the panels. The **Controls** panel starts
with quick actions for label and metadata-track visibility, followed by four
groups:

- **Layout**: zoom, automatic collapse threshold, and scale-bar visibility.
  Circular layout also provides opening, rotation, imported node angles, and
  opening/interior fill controls. **Node angles (degrees)** lists numeric
  attributes stored directly on tree nodes; **Automatic** uses TreeViz's
  computed angles.
- **Labels**: label font and size, support labels, and **Auto-cull overlaps**.
  Auto-cull overlaps (TOML
  `allow_label_overlap = false`) drops a label that would land on one already
  drawn; zooming in brings it back.
- **Branches & nodes**: **Tree width**, **Branch stroke width**, **Branch
  spacing**, **Colour by**, **Exact styling**, node circles, and **Pretty
  terminal branches**. Branch spacing scales row pitch in the rectangular
  layout. In the radial layout it shapes the angular split so crowded clades
  can receive more room. **Colour by** maps a numeric metadata column onto a
  scale or applies exact colours stored in node metadata. **Exact styling**
  maps node-circle diameter or colour and branch width or colour from data
  attributes. Wedge outlines follow the branch colour.
- **Metadata**: adjust metadata-track widths, row height, and gap. Add, remove,
  and edit the tracks themselves in **Tracks**.

Collapsed-wedge controls appear under **Branches & nodes** in the radial
layout. They include shape, fill source and opacity, gap, minimum body, overlap
policy, data-driven size, background outline, and label placement.

The Controls panel scrolls when it is taller than the stage; a thin scrollbar
marks the rows below the fold.

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
node's attributes under their display names, with a swatch for colour values.
Hovering or selecting a collapsed wedge outlines its polygon. The outline lies
inside the wedge and takes the same width cap as the wedge's own outline, so
it never crosses a neighbour and a thin wedge keeps its fill.

A collapsed clade's label sits past its wedge tip and reads along the branch
that enters the clade, walked back until 12 px of branch are in view so a stub
of a final segment does not turn it (**Collapsed wedge label direction**: **Along branch**,
the default) or out from the centre of the drawing (**Outward**; TOML
`collapsed_wedge_label_orientation = "bearing"`). With **Collapsed wedge
labels** set to **Leader lines** (`collapsed_wedge_label_declutter`), a label
that would land on another is pushed out along the line of its branch and joined
to its wedge by a thin leader line in the label's colour; **At wedge tip** seats every label at
its tip. See
[Tree styling](STYLING.md#label-colour-direction-and-position).

The search field (**Search taxa and clades…**) matches leaf names, leaf labels
and collapsed-clade labels. A hit inside a collapsed clade lands on that
clade's wedge. **Enter** zooms to the active hit (to at least 2x);
**Shift+Enter** and the arrow keys step through the hits; **Escape** clears
the search.

## Save And Export

Use `.treeviz.json` to preserve the full visualization. Use SVG, PNG, or PDF
for figures. Use Newick, Nexus, and metadata TSV exports for downstream data
exchange.

See [Exports](EXPORTS.md) for format guidance.

## Public Machine-Readable Files

The deployed app publishes:

- `https://treeviz.newlineages.com/version.json`
- `https://treeviz.newlineages.com/treeviz-command-schema.json`
- `https://treeviz.newlineages.com/treeviz-session.schema.json`
- `https://treeviz.newlineages.com/examples/manifest.json`

Use the session schema to validate `.treeviz.json` files generated by wrappers
or external pipelines before opening them in TreeViz.
