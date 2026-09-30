# Troubleshooting

## Metadata rows do not match leaves

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

## The tree is rejected for duplicate leaf labels

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

## A label reads against its neighbors

Set `label_flip` on that clade or drag the label; see
[Label color, direction, and position](STYLING.md#label-color-direction-and-position).
Two blocks of one polyphyletic phylum can land on either side of the turnover
and carry the same name in opposite directions. Flip or drag whichever of the
two reads worse.

## Collapsed wedges overlap or are too thin

Gap, outline, and overlap rules for wedges are described in
[Collapsed clades](STYLING.md#collapsed-clades).

- A wedge shows as a thin sliver when its clade has almost no angular room.
  Raise **Min body**, or size wedges by an attribute with **Size by** and
  **Size target** set to **Length** so every clade keeps its own slot.
- **Size by** with **Size target** set to **Width** is scaled down in a
  crowded fan. Set the target to **Length**.
- A clade background that reaches past its branches is a convex hull. Set
  **Background** to **Fitted**.
- Wedges that look like they overlap: read `wedgeOverlapPairs` and
  `wedgeBranchCrossings` from `window.__treeviz.getLayoutMetrics()` (open the
  app with `?api=1`). Zero for both means every fill is clear of its
  neighbors and of branches from other lineages. A count above zero, with the
  `metrics.wedge.overlap` warning, marks an obstacle the wedge could not clear
  at its smallest; set **Size target** to **Length** or raise **Branch
  spacing**.
- For crowding across the whole figure rather than one wedge, raise **Branch
  spacing**. In the radial layout it shapes the angle split, so a higher value
  keeps the drawing compact and it renders larger, which spreads the crowded
  labels apart.
- When the labels rather than the wedges collide, set **Collapsed wedge
  labels** to **Leader lines**; see
  [Label color, direction, and position](STYLING.md#label-color-direction-and-position).

## Labels are missing at the fitted view

When **Auto-cull overlaps** is ticked (TOML `allow_label_overlap = false`),
any label that would land on one already drawn is dropped. Zooming in helps:
above zoom 1, labels keep their screen size as the tree grows, and the culler
restores a label once it has room. To draw every label, for instance before a
large export, untick **Auto-cull overlaps**.

On a small viewport, the fitted zoom can fall below 1. Labels then shrink
along with the tree and look small at fit. Zoom in, or export at a larger
canvas.

## The inline notebook view is missing

A session is embedded inline when its encoded URL fragment is 256 KB or less,
which is roughly 1,500 tips with a few tracks. Anything larger is too large for
inline display; save it as `.treeviz.json` instead. The hosted app allows
framing (`frame-ancestors *`). If a self-hosted copy shows a blank iframe, the
usual cause is a `X-Frame-Options` or `frame-ancestors` header on that server.

```python
view = view_session(session, open_browser=False)
view.fragment
```

If `fragment` is `None`, save the session and open it in the browser.

## A figure has too much whitespace

Tune the layout before enlarging the canvas:

- reduce branch scale;
- reduce leaf spacing if labels still read clearly;
- reduce metadata gap;
- reduce label size when labels collide;
- enable auto-crop for static exports.

For automated checks, write crop metrics during rendering and inspect the
reported whitespace margins.

## Labels or tracks are clipped

Check the layout settings before you increase the canvas size. Labels, clade
annotations, metadata tracks, and legends all take up space. After the final
layout change, re-render and inspect the latest figure.

## Browser API is not available

Open TreeViz with `?api=1`:

```text
https://treeviz.newlineages.com/?api=1
```

Then wait for `window.__treeviz` before issuing commands.
