# Troubleshooting

## Metadata rows do not match leaves

Check the row-key column first. Its values should match the visible tree leaf
labels exactly unless you intentionally use normalization. After a leaf is
renamed in TreeViz, matching still uses its original imported identifier in
that session.

In the browser, read **Preview** during metadata import. For a complete table
that matches, **unmatched leaves** and **unmatched rows** should both be zero.
Choose **Cancel** to correct the file before importing. After import,
**Rebind leaves…** in the **Tracks** panel header reviews normalization and
matching. To change the row-key column, import the CSV or TSV again.

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
- When the labels rather than the wedges collide, set **Wedge labels** under
  **Collapsed wedges** to **Leader lines**; see
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

Open **Controls** and check **Show labels** and **Show metadata tracks**. In
**Tracks**, each track also has a **Visible** checkbox. If labels disappear
only when zoomed out, **Auto-cull overlaps** is hiding overlapping text.

Check the layout settings before you increase the canvas size. Labels, clade
annotations, metadata tracks, and legends all take up space. After the final
layout change, re-render and inspect the latest figure.

## The track kind I want is missing

The **+ Add Track** menu offers only the kinds that fit the column's inferred
type. Use `yes/no` for **binary-dots**; a column of only `0` and `1` is numeric.
A non-numeric column with 32 or fewer distinct values is categorical and offers
**color-strip**, not **text**. See [Values and types](METADATA.md#values-and-types).

## A file does not reopen after cancelling import

If choosing the same file again does nothing, drag the file onto the page. The
file picker may keep the previous selection after a cancel.

## I cannot find my previous session

**Previous sessions** in the **Sessions** panel belongs to the browser profile
that saved the work. A different browser, device, or private window does not
have those entries. Open an exported `.treeviz.json` file with **Add Tree** to
restore the work there. Clearing website data also removes browser-local
sessions.

## A link or example shows "Could not open the session"

TreeViz opens `?session=<url>` links only for files on the same site under
`/examples/` or `/sessions/`. When such a link does not open, or an example's
**Open session** button fails, the landing page (or the **Sessions** panel)
shows a red notice above the examples. It names the URL and gives the reason:

- **Not an allowed location**: the URL is outside those paths or on another
  site. Download the file and open it with **Add Tree**.
- **The server answered HTTP 404** (or another status): the file is not at that
  address. Check the path.
- **The response is not valid JSON**: the URL returned something other than a
  session. A note that the server returned a web page usually means the file
  does not exist and the site served its own page instead.
- **The file is not a valid TreeViz session**: the JSON parsed but is not a
  `.treeviz.json` session. The notice quotes the first problem found.
- **The request failed**: the browser could not reach the server.

A share link (`#s=...`) that does not open gets the same notice. It shows the
start and end of the fragment and its length, and says the link looks truncated
or corrupted, followed by the reason. Share links are often cut off when they
are copied out of a chat or an email. Ask for a fresh link or for the exported
`.treeviz.json` file.

Dismiss the notice with **×**. The examples and **Add Tree** stay available.

## Browser API is not available

Open TreeViz with `?api=1`:

```text
https://treeviz.newlineages.com/?api=1
```

Then wait for `window.__treeviz` before issuing commands.
