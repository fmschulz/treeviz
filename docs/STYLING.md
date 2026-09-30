# Styling

Styling in TreeViz is driven by data. The hosted browser, `.treeviz.json`
sessions, and `window.__treeviz` all share the same palette ids and style
fields, and sessions saved by earlier releases are migrated when they load. For
complete figures built from these settings, see the [Examples](EXAMPLES.md)
page.

TOML snippets on this page show the source-recipe form used to build saved
example sessions. The hosted browser does not load TOML directly. Use the
corresponding panel or browser API command, or open the compiled
`.treeviz.json` session.

## Palette registry

The web app ships a small static palette registry. Inspect it from the browser
API:

```js
window.__treeviz.palettes()
```

Each palette record contains:

- `id`: stable palette id accepted by sessions and browser commands.
- `label`: display label for UI controls.
- `role`: `categorical`, `sequential`, `diverging`, or `neutral`.
- `colors`: deterministic hex stops.
- `recommendedUse`: when to use the palette.
- `warnings`: limits such as category count or contrast caveats.
- `colorblindFriendly`: whether the palette is appropriate for common CVD use.
- `source`: source or inspiration note.

Current palette ids:

| Role          | IDs                                                                                 | Typical use                                                                        |
| ------------- | ----------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `categorical` | `okabe-ito`, `Set2`, `Tableau10`, `Dark2`, `Paired`, `Muted`, `ncldv-order-special` | unordered groups such as clade class, phenotype, environment, host, or domain      |
| `sequential`  | `Viridis`, `Magma`, `Cividis`, `Blues`                                              | ordered positive values such as abundance, support, load, or intensity             |
| `diverging`   | `RdBu`, `blue-orange`, `RdYlBu`, `PurpleGreen`, `BrBG`, `coolwarm`                  | centered signed values such as effects, residuals, contrasts, or score differences |
| `neutral`     | `gray`, `slate`, `soft-mono`                                                        | context, hidden branches, secondary tracks, and de-emphasized labels               |

Legacy spellings such as `viridis`, `tableau10`, `category10`, and
`diverging-rdbu` are accepted as aliases. New examples should use the ids in
the table.

## Track palettes

Browser API:

```js
await window.__treeviz.execute('track.update', {
  trackId: 'track-effect',
  patch: { palette: 'blue-orange', domain: [-3, 3] }
})
```

Python:

```python
tracks = [
    {"kind": "color_strip", "column_key": "phylum", "palette": "okabe-ito"},
    {"kind": "heatmap", "column_keys": ["log_fc", "effect"], "palette": "blue-orange"},
]
```

For exact category colors, use `categoryColors` in a session or command patch.
Exact colors are preserved in saved sessions and legends.

## Compact track symbols and wedges

Categorical `color-strip` tracks can keep their default strip display or render
each category as compact symbols or wedges:

```js
await window.__treeviz.execute('track.update', {
  trackId: 'track-host',
  patch: { displayMode: 'wedge', width: 16 }
})

await window.__treeviz.execute('track.update', {
  trackId: 'track-quality',
  patch: { displayMode: 'symbol', symbolShape: 'diamond', width: 18 }
})
```

Numeric `bar` tracks can be converted into interval symbols or wedges. Manual
bins are evaluated in order; `minInclusive` defaults to true and
`maxInclusive` defaults to false unless set explicitly. `autoBins` creates
equal-width bins across the track domain.

```js
await window.__treeviz.execute('track.update', {
  trackId: 'track-support',
  patch: {
    displayMode: 'symbol',
    symbolShape: 'circle',
    width: 18,
    bins: [
      { label: 'Low support', max: 60, color: '#d7191c', shape: 'dash' },
      {
        label: 'High support',
        min: 90,
        max: 100,
        maxInclusive: true,
        color: '#1a9641',
        shape: 'plus'
      }
    ]
  }
})

await window.__treeviz.execute('track.update', {
  trackId: 'track-abundance',
  patch: {
    displayMode: 'wedge',
    autoBins: 3,
    palette: 'Viridis',
    width: 18
  }
})
```

Get the track ids from `getSession().tracks`. The supported symbols are
`circle`, `square`, `triangle`, `diamond`, `plus`, and `dash`. For both symbols
and wedges, the legend keeps the category labels and the interval labels.

## Exact node and branch styling

Two Controls entries color branches. **Colour branches by** lists both the
numeric metadata columns, which map onto a color scale, and any node
metadata key whose values are colors (Newick `[&key=#rrggbb]` comments), which
apply as exact colors; a session that ships several colorings, such as one by
domain and one by a measured quantity, switches between them here. **Exact
styling** exposes the same exact-color attribute alongside the width and node
circle attributes. Setting one clears the other, so a scale and an exact
coloring never compete.

Map data attributes to node circles and branch strokes through the browser API:

```js
await window.__treeviz.execute('view.set-tree-style-attributes', {
  nodeDiameterAttribute: 'node_diameter',
  nodeColorAttribute: 'node_color',
  branchWidthAttribute: 'branch_width',
  branchColorAttribute: 'branch_color'
})

await window.__treeviz.execute('view.set-pretty-terminal-branches', {
  enabled: true
})
```

Diameter and branch-width values are in pixels. Internal nodes take their
values from node attributes such as Newick/Nexus annotations. Terminal leaves
check node attributes first and fall back to the bound metadata row.
`view.set-tree-style-attributes` sets all four attribute mappings, while pretty
terminal branches have a view command of their own.

Branch colors propagate toward the root. When all children of an internal
node resolve to the same color, the node takes that color too. As a result, a
monophyletic group is painted up to and including the stem of its last common
ancestor, and a group that is not monophyletic is painted up to each of its
largest monophyletic parts. The extension stops at any child without a color.
An internal node that has its own color value keeps it, and that value stands
for the color of its subtree. A color set on a clade by hand (Style > Branch
color in the browser, or a `[[branch_rule]]` `color`) overrides every
data-derived color on that clade and its descendants, so a recolored wedge or
clade always shows the new color. Reset clade style restores the data color.

## Layouts

The layouts are `rectangular`, `circular`, and `radial`. `radial` gives the
unrooted presentation. It places nodes by equal angle and then applies
equal-daylight sweeps, so every branch is drawn at its own length and in its
own direction, and no point is treated as the root.

The `circular` layout accepts a connector style. With `arc`, the default,
each node gets a polar elbow: an arc that spans its children, with a radial
spoke out to each one. With `straight`, a direct line joins parent and child.
Through TreeViz 0.3.1, this `straight` form was the layout named `radial`.
Sessions saved before that release are migrated onto it when they load.

```toml
[view]
layout = "circular"
connectors = "straight"
```

```js
await window.__treeviz.execute('view.set-layout', {
  layout: 'circular',
  connectors: 'straight'
})
```

Circular layouts can take imported angles from node attributes. The chosen
attribute must hold degrees from 0 through 360, and those values are mapped
into the current opening and rotation. A node with an invalid or missing value
falls back to automatic placement. Columns from the bound metadata table are
not used.

```js
await window.__treeviz.execute('view.set-layout', {
  layout: 'circular',
  circularOpeningAngle: 0,
  circularRotation: 90,
  circularAngleAttribute: 'paper_angle_degrees',
  showScaleBar: false
})
```

In the circular layout, **Controls > Layout** sets the **Opening angle**, which
leaves an empty sector, and the **Rotation**, which positions it. **Opening
fill** and **Interior fill** choose a color for each region; clear the
checkbox for transparency. Branches and clade backgrounds are drawn above the
interior fill. At openings of at least 90 degrees, track names appear
horizontally inside the gap. **Auto-fit to labels** closes the opposite edge
of the opening to those names. **Tip-to-track guides** connect terminal
branches to the inner metadata ring with thin dashed lines. The ranges and
defaults are in [Circular opening and fills](API.md#circular-opening-and-fills).

```toml
[view]
layout = "circular"
circular_opening_angle = 90
circular_rotation = 45
circular_opening_auto_fit = true
circular_opening_color = "#ffffff"
circular_interior_color = "#ffffff"
```

To go back to automatic angles, pass `circularAngleAttribute: null`. The
distance scale can be hidden with `showScaleBar: false`, which leaves branch
geometry unchanged. In TOML, set `show_scale_bar = false` under `[view]`.

If a radial tree has saved source positions, select **Node X coordinate** and
**Node Y coordinate** in **Controls > Layout**. Both fields read direct node
metadata. Each node needs both coordinates, given as finite numbers or
nonempty numeric strings, and positive Y points down. In the API, the matching
`view.set-layout` fields are `radialXAttribute` and `radialYAttribute`. To
return to automatic placement, choose **Automatic** for both fields. Automatic
placement is also used, and `render.radial-coordinates-invalid` is reported,
when the key pair is incomplete or any coordinate is missing, Boolean, blank,
nonnumeric, or nonfinite. Zoom, pan, and fit still work with the camera.
The rectangular and circular layouts ignore both coordinate fields.

`leaf_spacing` (Controls: **Branch spacing**) controls how much room each leaf
receives. In the rectangular layout, it scales the row pitch. The radial layout
has only a full turn to divide, so there the setting shapes how the angle is
split: each child is weighted by its leaf count raised to this power. Values
above 1 give wide clades more of the turn. The drawing stays compact, renders
larger, and crowded regions gain room. Values below 1 even out the shares, so
wide clades reach further and the drawing inflates. Imported radial positions
ignore both this setting and the branch-length mode.

```toml
[view]
layout = "radial"
leaf_spacing = 1.6
```

## Collapsed clades

Collapsed clades are drawn as wedges. The outline uses the clade's effective
branch color and width. In the rectangular and circular layouts, the wedge is
a triangle or an annulus sector. In the radial layout, the wedge follows the
space that the expanded subtree occupies, and the keys below shape it.

A clade can be collapsed in the browser (`tree.collapse-clade`) or through a
config attribute. When `collapse_attribute` is set, each non-root internal node
with a truthy node attribute value for that key compiles to a collapsed clade.
Truthy means present and not `""`, `"0"`, or `"false"`. This covers nodes that
name-based `[[branch_rule]]` selectors cannot reach, for example many clades
that share one name.

```toml
[view]
collapse_attribute = "collapse"
collapsed_wedge_shape = "rounded"      # or "triangle"
collapsed_wedge_fill = "background"    # or "branch", or "attribute" (color from a node attribute)
collapsed_wedge_fill_attribute = "fc"  # color attribute that the "attribute" fill reads
collapsed_wedge_fill_opacity = 0.28    # branch/attribute fill opacity; raise it when the fill carries data
collapsed_wedge_gap = 6                # px kept between neighboring wedges
collapsed_wedge_min_body = 5           # px half-width floor
collapsed_wedge_min_body_from_branch = false  # true: body never thinner than the entering branch
collapsed_wedge_allow_overlap = false  # true keeps crowded wedges as first shaped
collapsed_wedge_size_attribute = "pd"  # size wedges from node attributes instead
collapsed_wedge_size_scale = "log"     # "linear" or "log" (log10)
collapsed_wedge_size_target = "width"  # or "length" to size the wedge's reach
collapsed_wedge_size_range = [10, 80]  # px, outer-edge width or length
clade_background_outline = "hull"      # or "fitted"
```

- `rounded` (default) insets each wedge by half the gap so neighbors stay
  apart. It rounds the outline and shrinks a wedge that still meets a
  neighbor or a branch of another lineage.
- `triangle` draws the plain triangle from the clade root to the extreme tips.
- Either shape thickens a footprint thinner than the minimum body, so a
  two-tip clade reads as a rod rather than a line.
- The outline is painted inside the fill's edge and never reaches into a
  neighboring wedge. Its width follows the branch stroke, capped so a thin
  wedge keeps a visible fill. Hover and selection outlines use the same cap.
- `collapsed_wedge_min_body_from_branch = true` (session
  `collapsedWedgeMinBodyFromBranch`, default `false`) outlines each wedge at
  the stroke width of the branch that enters it. It widens the wedge until two
  such outlines and a hairline of fill fit inside, also under crowding. A wedge
  too short to hold them keeps the capped outline. Width-sized wedges are
  exempt, since their outer edge carries the value.
- Gap, minimum body and size range are pixels at full tree scale. When a larger
  label font takes more of the radius, the tree and every wedge shrink by the
  same factor.
- A wedge keeps the gap from its neighbors and from the center line of any
  branch of another lineage. The branch stroke plays no part: a wide stroke
  eats into the gap, not into the fill.
- `collapsed_wedge_fill` picks the fill. `background` (default) takes the
  nearest enclosing `clade_background`, or the branch color where there is
  none. `branch` takes the wedge's own branch color, translucent, which tells
  wedges apart when several sit on one painted clade. `attribute` reads the
  fill from `collapsed_wedge_fill_attribute`, a node attribute holding a color, so the
  fill can encode something other than the outline; a clade without a value
  under that key keeps the `background` fill. `collapsed_wedge_fill_opacity`
  sets the translucency of the `branch` and `attribute` fills (default 0.28, a
  tint); a fill that carries its own data reads better around 0.8. A collapsed
  clade's own `wedgeFill` clade style (Style > Wedge fill on a right-clicked
  wedge) replaces the mode's fill for that wedge.
- The local `wedgeFillGradient` style accepts `{ startColor, endColor }` and
  takes precedence over the solid fill, mode and opacity. Its colors interpolate
  from the clade root to the outer edge. `cladeBackgroundGradient` uses the same
  two-color form for an expanded clade's background. In TOML use
  `wedge_fill_gradient` or `clade_background_gradient`, with `start_color` and
  `end_color`. These styles are set through the API or config; they do not
  inherit to child clades. Endpoints accept `#rrggbb` and `rgba(r,g,b,a)`; use
  the latter for alpha. A zero-length gradient renders as solid `endColor`.
- `collapsed_wedge_size_attribute` replaces the footprint width with a data
  value: the wedge runs out to its footprint depth and its outer-edge width is
  the value mapped (as-is, or after `log10`) from the range of values across
  the collapsed clades onto `collapsed_wedge_size_range`. A width-sized wedge
  is neither inset nor thickened, because its outer edge is the value itself.
  Clades without a numeric value, and values of zero or below under `log`,
  keep the footprint wedge.
- `collapsed_wedge_size_target` chooses the dimension. `width` (default) puts
  the value in the outer edge. A radial fan constrains that: the angular room
  around each clade belongs to its neighbors, so widths that collide are all
  scaled down by one shared factor, keeping their proportions exact while the
  absolute pixel mapping shrinks. `length` puts the value in the reach from the
  clade root to the base and keeps each clade's own angular slot, so a
  colliding wedge is pulled back on its own and the mapping is left alone. It
  gives up length against neighboring wedges and branches of other lineages
  down to its footprint depth, then narrows its base about the axis down to
  the minimum body. An obstacle it cannot clear even then is left in place
  and counted by `getLayoutMetrics()` as `wedgeOverlapPairs` and
  `wedgeBranchCrossings`; see [Browser API](API.md#layout-qa-pattern).
  `collapsed_wedge_allow_overlap = true` keeps the mapped sizes and permits the
  overlap.
- `collapsedWedgeLengthMode` sets the length of a width-sized wedge. It has no
  TOML key; set it with the `lengthMode` argument of
  `view.set-collapsed-wedge-options`. `footprint` (default) runs the wedge out
  to its footprint depth. `max-path` runs it out to the longest summed
  root-to-tip path in the clade. `max-path` applies only in the radial layout
  with branch lengths shown and `collapsed_wedge_size_target = "width"`.
- `clade_background_outline` picks how a `clade_background` is outlined in the
  radial layout. `hull` (default) draws the convex hull of the clade with a
  faint outline. `fitted` draws a soft buffer that follows the branches and
  wedges themselves, with no outline: the buffer is several overlapping shapes
  in one path, and a stroke would draw the seams where they cross.

For `session.restore`, each key has a camelCase counterpart on the session
view: `collapsedWedgeShape`, `collapsedWedgeFill`,
`collapsedWedgeFillAttribute`, `collapsedWedgeFillOpacity`,
`collapsedWedgeGap`, `collapsedWedgeMinBody`,
`collapsedWedgeMinBodyFromBranch`, `collapsedWedgeAllowOverlap`,
`collapsedWedgeSizeAttribute`, `collapsedWedgeSizeScale`,
`collapsedWedgeSizeTarget`, `collapsedWedgeSizeRange`,
`cladeBackgroundOutline`, `collapsedWedgeLabelDeclutter`,
`collapsedWedgeLabelOrientation`, `allowLabelOverlap`, and `showNodeCircles`.
The `view.set-collapsed-wedge-options` command patches the wedge settings
using short names: `shape`, `fill`, `fillAttribute`, `fillOpacity`, `gap`,
`minBody`, `allowOverlap`, `sizeAttribute`, `sizeScale`, `sizeTarget`,
`lengthMode`, `sizeRange`, `outline`, `labelDeclutter`, `labelOrientation`.
When a collapsed clade has a data-defined node circle
(`node_diameter_attribute`), the circle is drawn just past the outer edge of
the wedge. Setting `show_node_circles = false` (Controls > Show node circles)
hides all data-defined circles but leaves the attribute set. If the root node
of a collapsed clade is named, that name labels the clade just past the wedge
tip whenever labels are shown (Controls > Show labels). The section
[Label color, direction, and position](#label-color-direction-and-position)
explains which way the label reads. Leaf labels must stay unique, so to give a
single-taxon clade drawn as a leaf a readable name, use a `[[branch_rule]]`
with a `label` selector and a `clade_label`, which then replaces the leaf's
displayed name.

## Label color, direction, and position

On a `[[branch_rule]]`, `label_color` sets the text color for every label in
the matched subtree. That includes leaf labels and the wedge label of any
collapsed clade inside it.

```toml
[[branch_rule]]
clade = "Bacteria"
label_color = "#163e8a"
```

A collapsed clade's label sits just past the tip of its wedge, beyond any node
circle. By default it reads along the branch that enters the clade. TreeViz
walks that branch back until at least 12 px of it are in view, so a short stub
at the end does not turn the label. When several wedges share a bearing, their
labels land on top of each other, and no wedge length or angle setting can fix
that. `collapsed_wedge_label_declutter` (Controls: **Collapsed wedge labels**
set to **Leader lines**) pushes a label that overlaps an already placed one
further out along the line of its branch until it clears. The push follows the
bearing instead when that line is blocked, or when the direction is
**Outward**. The leader then continues the branch, and crowded labels stack in
rings. Each pushed label gets a thin leader line back to its wedge, drawn in
the label's own color:

```toml
[view]
collapsed_wedge_label_declutter = true
```

It is off by default (**At wedge tip**) and does nothing to a figure whose
labels already clear each other.

`collapsed_wedge_label_orientation` (Controls: **Collapsed wedge label
direction**) sets the reading direction of the label. Under either value, the
label is seated at the wedge tip. With `branch` (the default, **Along
branch**), the text turns to follow the branch that enters the clade, for every
clade whose root has a parent, so a figure's labels read the way their branches
run. With `bearing` (**Outward**), the text points out from the center of the
drawing, like a spoke. A declutter push moves the label along its entering
branch under `branch`. It moves outward along the bearing when that line is
blocked, or under `bearing`. A leader connects the label to the seat it would
have had. A clade whose root has no parent reads outward under both values.

```toml
[view]
collapsed_wedge_label_orientation = "bearing"
```

With `allow_label_overlap = false` (Controls: **Auto-cull overlaps**; view
`allowLabelOverlap`), a label that would land on one already drawn is dropped.
For a collapsed clade, the culler checks the label at its decluttered seat, so
a pushed label that clears its neighbors stays. Culled labels come back as you
zoom in. Above zoom 1, labels keep their screen size while the tree grows,
which opens room between them. The default is `true`.

```toml
[view]
collapsed_wedge_label_declutter = true
allow_label_overlap = false
```

So that text is never upside down, labels on the far side of the figure turn
around. A clade that sits right where this rule flips then reads against its
neighbors. To reverse the choice for one label, use `label_flip`:

```toml
[[branch_rule]]
clade = "Bdellovibrionota"
label_flip = true
```

Any label can also be dragged. Press on the text and move it. TreeViz stores the
offset on that clade as `cladeLabelOffsetX` and `cladeLabelOffsetY`, so it is
kept when the session is saved and shows up in exports. To set the same values
from the browser API:

```js
await window.__treeviz.execute('tree.style-clade', {
  stableKey,
  patch: { cladeLabelOffsetX: 18, cladeLabelOffsetY: -6, labelFlip: true }
})
```

The position of a clade annotation is set by `cladeLabelPlacement`. The TOML
key is `clade_label_placement` on a `[[branch_rule]]`, and it takes the same
values. **Style clade > Clade annotation** offers `clade` and `node`.

- `clade` (default) places the label past the clade's tips, with a white
  backing and a reserved label lane before metadata tracks.
- `node` centers a horizontal annotation on an internal or terminal node. It
  uses the clade label's text, color, weight, font size, and offsets without
  reserving a label lane or drawing the white backing. A terminal node gets
  one label instead of a duplicate tip label.
- `background-top`, `background-top-left`, `background-top-right`,
  `background-left`, and `background-right` apply in the radial layout to a
  clade with a drawn background, solid or gradient. The label sits unrotated
  at that seat on the background. It replaces a collapsed clade's wedge label,
  so the name is not drawn twice. Other layouts treat these values as `clade`.

`cladeLabelFontSize` accepts fractional values from 1 to 96 pixels.

`cladeBackgroundPadding` gives the padding, in pixels, of a single clade's
fitted radial background (`clade_background_outline = "fitted"`). Values must
be nonnegative; leave it out to get automatic padding. This is a clade style
field used by sessions and `tree.style-clade`, and there is no TOML key for
it.

```js
await window.__treeviz.execute('tree.style-clade', {
  stableKey,
  patch: {
    label: 'Bacillaceae',
    cladeLabelPlacement: 'node',
    cladeLabelFontSize: 4.5,
    cladeLabelColor: '#111111'
  }
})
```

## Connections

Each connection set draws either bowed, tapered ribbons or straight lines of
constant width. The default is `ribbon`; to get lines, set
`geometry: 'straight'` on the session connection set. Pair-level `color`,
`width`, and `opacity` work with both geometries.

Endpoints are matched by exact, case-sensitive node name. A leaf match wins;
failing that, the internal-node name has to be unique. Endpoints that are
hidden, collapsed, ambiguous, or unbound are left out and reported in the
render diagnostics. For the JSON shape and the diagnostic codes, see
[Connections](API.md#connections).

## Legends and attribute names

Attribute encodings (branch color, node-circle color, and wedge fill from a
node attribute) have no legend of their own, and the Controls pickers show
their keys exactly as written in the tree. `[[legend]]` tables add hand-written
legends, placed after the legends derived from tracks, markers, node marks, and
connections. These appear in the Legend panel, in the in-figure legend, and in
exports. A legend's `shape` is either `square` (the default, a swatch list) or
`circle`. Circle entries take an optional `size`, which is the circle diameter
in pixels (default 10). `[attribute_labels]` maps a node attribute to the name
shown in the pickers and hover tooltips, as `Name (key)`. With
`figure_legend = true`, the in-figure legend opens when the session loads.

```toml
[view]
figure_legend = true

[attribute_labels]
vc = "Domain color"
cc = "Culturedness color"
fcol = "Isolate color"

[[legend]]
title = "Domain"
entries = [
  { label = "Bacteria", color = "#1f5fd0" },
  { label = "Archaea", color = "#00ced1" },
  { label = "Eukaryota", color = "#6b8e23" }
]
```

In the session document, `[[legend]]` tables compile to a top-level `legends`
array of `{ title, shape?, entries: [{ label, color, size? }] }`.
`[attribute_labels]` compiles to a top-level `attributeLabels` map from key to
name, and `figure_legend` compiles to `view.figureLegendVisible`. Because no
command edits `legends` or `attributeLabels`, set them in the document and load
it with `session.restore`. To show, hide, or move individual sections, use
`view.set-figure-legend-placement`. Section settings made explicitly take
precedence over the global `view.set-figure-legend-visibility` and
`view.toggle-figure-legend` commands.

Session JSON can also hold a continuous scale legend. It uses
`kind: 'continuous-scale'` with `title`, `axisLabel`, `colors`, `domain`,
`sizeRange`, `transform`, and `ticks`, plus the optional `scale`,
`orientation`, and `secondaryAxis`. By default `orientation` is `vertical`. A
horizontal ramp runs from low to high, left to right, and its primary ticks and
axis label sit upright below it. If present, the `secondaryAxis` (`axisLabel`,
`domain`, `transform`, `ticks`) is drawn upright above the ramp. The size range
must be nondecreasing with a positive maximum, and equal positive values give a
rectangular ramp. `scale` accepts finite values from `0.1` to `4` and defaults
to `1`. It scales the ramp, spacing, strokes, axes, ticks, and text. The
session shape and validation rules are in
[Browser API](API.md#continuous-attribute-legends). TOML `[[legend]]` covers
square and circle legends only; it does not support continuous scales.

## Conditional style rules

Conditional style rules are for cases where metadata values need thresholds,
bins, or category logic rather than exact visual values. The rules apply in
order, and when two rules set the same style target on the same node or branch,
the later rule wins.

```js
await window.__treeviz.execute('view.set-conditional-style-rules', {
  rules: [
    {
      id: 'high-abundance-branch',
      source: 'abundance',
      condition: { kind: 'interval', min: 10 },
      target: 'branch-width',
      value: 4
    },
    {
      id: 'soil-labels',
      source: 'host',
      condition: { kind: 'exact', value: 'soil' },
      target: 'label-color',
      value: '#1d4ed8'
    },
    {
      id: 'top-abundance-symbol',
      source: 'abundance',
      condition: { kind: 'rank', top: 1 },
      target: 'symbol',
      value: {
        shape: 'diamond',
        color: '#7b3294',
        size: 9,
        label: 'Top abundance'
      }
    }
  ]
})
```

Supported conditions:

- `exact`: match a string, number, boolean, or missing value.
- `interval`: numeric range with optional `minInclusive` and `maxInclusive`.
- `quantile`: numeric quantile fraction range from 0 to 1.
- `rank`: top or bottom numeric ranks.
- `missing`: missing, null, undefined, or blank string.
- `boolean`: boolean values; string forms such as `true`, `false`, `yes`, and
  `no` are accepted.
- `contains`: text contains; case-insensitive by default.
- `regex`: JavaScript regular expression pattern and optional flags.

`branch-color` rules extend to ancestors the same way `branch_color_attribute`
does (see [Exact node and branch styling](#exact-node-and-branch-styling)).

The rendered targets are `branch-color`, `branch-width`, `node-color`,
`node-size`, `internal-marker-color`, `internal-marker-size`, `label-color`,
`label-weight`, and `label-visibility`. The `symbol`, `wedge`, and
`track-bar-color` targets are stored in sessions and resolved for compact track
workflows. Whether a track uses compact display is set by its `displayMode`.
