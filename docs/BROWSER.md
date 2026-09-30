# Browser usage

TreeViz runs as a static browser app.

## Open

- [https://treeviz.newlineages.com/](https://treeviz.newlineages.com/) opens
  the app.
- [https://treeviz.newlineages.com/?api=1](https://treeviz.newlineages.com/?api=1)
  also exposes the `window.__treeviz` browser API.
- [https://treeviz.newlineages.com/?mode=headless&api=1](https://treeviz.newlineages.com/?mode=headless&api=1)
  is a render-only mode for automation. It exposes the same API.
- `https://treeviz.newlineages.com/?session=/examples/<id>/session.treeviz.json`
  opens a saved session. TreeViz opens `?session=` files only from the same
  site, under `/examples/` or `/sessions/`.
- A **Share** link carries a copy of the session in a `#s=` fragment. Anyone
  with the complete link can open it.

When a `?session=` or share link does not open, the page shows a **Could not
open the session** notice with the reason. See
[Troubleshooting](TROUBLESHOOTING.md#a-link-or-example-shows-could-not-open-the-session).

## Header

The header holds a sun/moon button, **Add Tree**, **Sessions**, and **Share**.
The sun/moon button switches between the light and dark theme. Until you press
it, TreeViz follows the system color scheme. After you press it, this browser
stores the choice for later visits.

## Load data

TreeViz accepts:

- Newick (including IQ-TREE `.contree`) and Nexus tree files;
- `.treeviz.json` sessions;
- TSV/CSV metadata tables with one header row;
- gzipped (`.gz`) copies of any of these files.

Drop files onto the page or use the file picker. Load the tree first, then
the metadata, and choose the row-key column that matches metadata rows to tree
leaves.

**Add Tree** opens the file picker for every supported type, including metadata
tables and saved sessions. A tree file with several trees opens a picker; select
the tree to load. Opening another tree while one is loaded shows a **Replace
tree** review. Save the current session first, then check **I understand** and
click **Import**.

## Configure the view

Metadata tracks show table values beside the leaves. Categories get color
strips, continuous values get gradients and heatmaps, numeric comparisons get
bars, labels get text tracks, and presence and absence get binary dots. In the
**Tracks** panel, each track appears under its title. Expand one to edit its
columns, palette, width, and other settings. When the panel appears, the first
track is already open. You add and remove tracks from the same panel. Once the
session has metadata, the panel header shows **Rebind leaves…** next to **+ Add
Track**. It reopens the leaf-to-metadata review, so normalization and matching
change without a new import. To change the row-key column, import the table
again.

The stage toolbar provides controls to switch the layout, turn **Auto size** on
or off, fit the tree, search taxa and clades, show or hide branch lengths, and
open the panels. The toolbar holds a few layout-specific settings as well: tip
alignment in the rectangular layout, and arc or straight connectors in the
circular layout. It is also where you save and restore named views.

The toolbar has two rows. The first row holds **Rect | Circular | Radial**,
**Auto size**, **Fit**, the search field, **Phylo | Clado** (branch lengths),
**Tip | Label** or **Arc | Straight**, and **Views**. **Auto size** turns off
when you set the tree width or branch spacing by hand in **Controls**. The
second row opens **Controls**, **Tracks**, **Legend**, **Commands** (the command
palette), **Export**, and the keyboard shortcut list (**?**). At a viewport
width of 640 px or less, a **More ▾** button on each row holds the branch-length,
alignment or connector, and **Views** controls on the first row, and
**Commands**, **Export**, and **?** on the second.

The
**Controls** panel opens with quick actions for label and metadata-track
visibility. Four groups follow them:

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

Any label can be dragged to a new position by pressing on its text and moving
it. The offset is stored on that clade, which means it survives saving and
appears in exports.

To change a single node, double-click a leaf or internal node to open the
**Inspector**, and adjust its branch, circle, and label controls. `Ctrl+I`
(`⌘I` on macOS) also opens and closes the Inspector. Right-click a node for
clade actions such as **Rename leaf**, **Annotate clade…**, **Style clade**, and
**Collapse clade**. Saved views let you keep
more than one arrangement of the same session. [Tree styling](STYLING.md)
lists every option.

The **Legend** panel starts with the legends derived from tracks, markers, node
marks, and connections. After those come any hand-written legends stored on the
session (`legends`, from `[[legend]]` tables in a TOML config). The star button
beside a section, **Display in figure**, places a section on the canvas, and that in-figure legend is included
in SVG, PNG, and PDF exports. Session JSON can also provide a continuous
size/color legend. In the figure, that section is drawn without a frame and with
the title above the ramp, while the side panel shows it in its normal container.

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

Hover over a leaf, an internal node or a collapsed wedge to see a tooltip.
It shows the label or name, `N leaves` for a wedge, `Branch length x` and
`Support y`, followed by the node's attributes under their display names.
Color values come with a swatch. Hovering over or selecting a collapsed wedge
outlines its polygon.

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

Type in the search field (**Search taxa and clades…**) to match leaf names, leaf
labels, and collapsed-clade labels. When a hit sits inside a collapsed clade,
the search lands on that clade's wedge. Press **Enter** to zoom to the active
hit (to at least 2x), use **Shift+Enter** or the arrow keys to step through the
hits, and press **Escape** to clear the search.

Press `?` to list the keyboard shortcuts. `/` or `Ctrl+F` opens the search
field, `Ctrl+K` opens the command palette, `=` and `-` zoom, and the arrow keys
pan. On macOS, `⌘` replaces `Ctrl`. Single-key shortcuts do nothing while a
text field has focus, so those characters go into the field. `Ctrl+K`, `Ctrl+F`,
and `Ctrl+I` still work from a text field.

## Save and export

Save a `.treeviz.json` file to preserve the full visualization. For
figures, export SVG, PNG, or PDF. For downstream data exchange, the Newick,
Nexus, and metadata TSV exports are the right choice. All of these are in the
**Export** dialog; the session file is **Export Session (JSON)**.

**Sessions** lists the public examples and the sessions saved in this browser
profile. Other visitors do not see those saved sessions. **Share** makes a link
that contains a copy of the session. Export a session file to keep a copy
outside browser storage.

See [Exports](EXPORTS.md) for format guidance.

## Public machine-readable files

The deployed app publishes:

- `https://treeviz.newlineages.com/version.json`
- `https://treeviz.newlineages.com/treeviz-command-schema.json`
- `https://treeviz.newlineages.com/treeviz-session.schema.json`
- `https://treeviz.newlineages.com/examples/manifest.json`

Use the session schema to validate `.treeviz.json` files generated by wrappers
or external pipelines before opening them in TreeViz.
