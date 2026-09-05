# Troubleshooting

## Metadata Rows Do Not Match Leaves

Check the row-key column first. Its values should match the visible tree leaf
labels exactly unless you intentionally use normalization.

Common causes:

- the wrong row-key column was selected;
- metadata uses different case or underscores than the tree labels;
- tree labels contain prefixes, suffixes, or quoted-label decorations;
- metadata has rows for leaves that are not in the tree;
- the tree has leaves that are missing from metadata.

In Python, inspect:

```python
from treeviz import binding_diagnostics

binding_diagnostics(session)
```

In the browser API, inspect diagnostics after metadata import:

```js
window.__treeviz.getDiagnostics()
```

## The Tree Is Rejected For Duplicate Leaf Labels

Leaf names must be unique. The parser reports `parse.duplicate-leaf-label` and
loads nothing. Rename the leaves in the file, or keep unique identifiers as
leaf names and attach the display text as a clade label:

```toml
[[branch_rule]]
label = "GB_GCA_024275655.1"
clade_label = "B1Sed10-29"
```

In the browser API the same effect is `tree.style-clade` with
`{ patch: { label: "B1Sed10-29" } }`.

## A Label Reads Against Its Neighbours

In the polar layouts a label reads outward from the centre, and text on the far
side turns around so it is never upside down. A clade sitting where that rule
turns over reads the opposite way from the clades beside it. Set `label_flip`
on that clade to reverse the choice, or drag the label clear:

```toml
[[branch_rule]]
clade = "Bdellovibrionota"
label_flip = true
```

Two blocks of one polyphyletic phylum can land on either side of that turnover
and carry the same name in opposite directions. Flip or drag whichever of the
two reads worse.

## Collapsed Wedges Overlap Or Are Too Thin

In the radial layout wedges do not overlap unless **Allow overlap** is on in
the collapsed-wedge settings under **Controls**. Neighbouring wedges are shrunk
until they clear each other by **Gap**.

- A wedge shows as a thin sliver when its clade has almost no angular room.
  Raise **Min body**, or size wedges by an attribute with **Size by** and
  **Size target** set to **Length** so every clade keeps its own slot.
- **Size by** with **Size target** set to **Width** is scaled down in a
  crowded fan. Set the target to **Length**.
- A clade background that reaches past its branches is a convex hull. Set
  **Background** to **Fitted**.
- For crowding across the whole figure rather than one wedge, raise **Branch
  spacing**. In the radial layout it shapes the angle split, so a higher value
  keeps the drawing compact and it renders larger, which spreads the crowded
  labels apart.
- When it is the labels rather than the wedges that collide, set
  `collapsed_wedge_label_declutter`. Wedges that share a bearing seat their
  labels on top of each other, and no wedge length or spacing value separates
  them; the declutter pass pushes each colliding label further out along its
  own bearing until it clears and draws a leader line back to the wedge.

## Labels Are Missing At The Fitted View

With **Auto-cull overlaps** ticked (TOML `allow_label_overlap = false`) a label
that would land on one already drawn is dropped. Zoom in: labels keep their
screen size above zoom 1 while the tree grows, and the culler brings a label
back once it has room. Untick **Auto-cull overlaps** to draw every label,
for instance before a large export.

On a small viewport the fitted zoom can be below 1. Labels then shrink with the
tree and read small at fit; zoom in, or export at a larger canvas.

## validate_session Rejects A Session Saved From The App

The package schema is behind the hosted app: it lacks the view fields
`showNodeCircles`, `collapsedWedgeFillAttribute`, `collapsedWedgeFillOpacity`
and `collapsedWedgeLabelDeclutter`, the `attribute` value of
`collapsedWedgeFill`, and the top-level `legends` and `attributeLabels`. The
error names them as unexpected properties or an invalid enum value. Validate
the file against the live schema at
`https://treeviz.newlineages.com/treeviz-session.schema.json` instead; see
[Schema Compatibility](PYTHON.md#schema-compatibility).

## The Inline Notebook View Is Missing

Sessions up to 256 KB of encoded URL fragment (roughly 1,500 tips with a few
tracks) are embedded inline. Larger sessions are too large for inline display
and should be saved as `.treeviz.json` instead. The hosted app allows framing
(`frame-ancestors *`); a blank iframe on a self-hosted copy usually means a
`X-Frame-Options` or `frame-ancestors` header on that server.

```python
view = view_session(session, open_browser=False)
view.fragment
```

If `fragment` is `None`, save the session and open it in the browser.

## A Figure Has Too Much Whitespace

Tune the layout before enlarging the canvas:

- reduce branch scale;
- reduce leaf spacing if labels still read clearly;
- reduce metadata gap;
- reduce label size when labels collide;
- enable auto-crop for static exports.

For automated checks, write crop metrics during rendering and inspect the
reported whitespace margins.

## Labels Or Tracks Are Clipped

Increase canvas size only after checking layout settings. Labels, clade
annotations, metadata tracks, and legends all need space. Re-render after the
final layout change and inspect the latest figure.

## Browser API Is Not Available

Open TreeViz with `?api=1`:

```text
https://treeviz.newlineages.com/?api=1
```

Then wait for `window.__treeviz` before issuing commands.
