# Styling

TreeViz styling is data-first. The hosted browser, `.treeviz.json` sessions,
and `window.__treeviz` use the same palette ids and style fields.
Sessions written by earlier releases are migrated on load. Complete figures
built from these settings are on the [Examples](EXAMPLES.md) page.

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

Read the track ids from `getSession().tracks`. Supported symbols are `circle`,
`square`, `triangle`, `diamond`, `plus`, and `dash`; legends preserve category
labels and interval labels for symbols and wedges.

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

Diameter and branch-width values are pixels. Internal nodes read node attributes
such as Newick/Nexus annotations; terminal leaves read node attributes first and
then the bound metadata row. `view.set-tree-style-attributes` sets the four
attribute mappings. Pretty terminal branches are a separate view command.

Branch colors extend upward. An internal node whose children all resolve to
the same color takes that color, so a monophyletic group is painted up to and
including the stem of its last common ancestor, and a group that is not
monophyletic is painted up to each of its largest monophyletic parts. A child
without a color stops the extension. Internal nodes with their own color value
keep it, and that value counts as the color of their subtree. A color set on a
clade by hand (Style > Branch color in the browser, or a `[[branch_rule]]`
`color`) wins over every data-derived color on that clade and its descendants,
so recoloring a wedge or clade always shows; Reset clade style brings the data
color back.

## Layouts

`rectangular`, `circular`, and `radial`. `radial` is the unrooted presentation:
equal-angle placement followed by equal-daylight sweeps, so each branch is drawn
at its own length in its own direction and no point is privileged as the root.

`circular` takes a connector style. `arc` (the default) draws the polar elbow,
an arc across each node's children with a radial spoke out to each one.
`straight` joins parent to child directly.

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

Circular layouts can read imported angles from node attributes. The
selected attribute must contain degrees from 0 through 360. Values map into the
current opening and rotation; invalid or missing values fall back to automatic
placement for that node. Bound metadata-table columns are not used.

```js
await window.__treeviz.execute('view.set-layout', {
  layout: 'circular',
  circularOpeningAngle: 0,
  circularRotation: 90,
  circularAngleAttribute: 'paper_angle_degrees',
  showScaleBar: false
})
```

Pass `circularAngleAttribute: null` to return to automatic angles. Setting
`showScaleBar: false` hides the distance scale without changing branch
geometry. The TOML equivalent is `show_scale_bar = false` under `[view]`.

For a radial tree with saved source positions, select **Node X coordinate**
and **Node Y coordinate** in **Controls > Layout**. These use direct node
metadata. Every node needs both coordinates as finite numbers or nonempty
numeric strings; positive Y points down. The API uses `radialXAttribute` and
`radialYAttribute` in `view.set-layout`. Choose **Automatic** for both fields
to resume automatic placement. An incomplete key pair, or any missing,
Boolean, blank, nonnumeric, or nonfinite coordinate, uses automatic placement
and reports `render.radial-coordinates-invalid`. The camera still supports
zoom, pan, and fit.
Rectangular and circular layouts ignore the two coordinate fields.

`leaf_spacing` (Controls: **Branch spacing**) sets how much room each leaf
gets. In the rectangular layout it scales the row pitch. The radial layout has
only a full turn to give, so there it shapes the angle split: each child is
weighted by its leaf count raised to this power. Above 1 the wide clades take
more of the turn, which keeps the drawing compact so it renders larger and
crowded regions gain room; below 1 the shares even out and wide clades reach
further, inflating the drawing. Imported radial positions ignore this setting
and the branch-length mode.

```toml
[view]
layout = "radial"
leaf_spacing = 1.6
```

## Collapsed clades

Collapse a clade from the browser (`tree.collapse-clade`) or from a config
attribute. With `collapse_attribute`, every non-root internal node whose
node attribute value for that key is truthy (present and not `""`, `"0"`,
or `"false"`) compiles to a collapsed clade. This reaches nodes that name-based
`[[branch_rule]]` selectors cannot, such as many clades sharing one name.

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
  the collapsed clades onto `collapsed_wedge_size_range`. Clades without a
  numeric value, and values of zero or below under `log`, keep the footprint
  wedge.
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

Each key has a camelCase counterpart on the session view for
`session.restore`: `collapsedWedgeShape`, `collapsedWedgeFill`,
`collapsedWedgeFillAttribute`, `collapsedWedgeFillOpacity`,
`collapsedWedgeGap`, `collapsedWedgeMinBody`,
`collapsedWedgeMinBodyFromBranch`, `collapsedWedgeAllowOverlap`,
`collapsedWedgeSizeAttribute`, `collapsedWedgeSizeScale`,
`collapsedWedgeSizeTarget`, `collapsedWedgeSizeRange`,
`cladeBackgroundOutline`, `collapsedWedgeLabelDeclutter`,
`collapsedWedgeLabelOrientation`, `allowLabelOverlap`, and `showNodeCircles`.
The command `view.set-collapsed-wedge-options` patches these wedge settings
under short names: `shape`, `fill`, `fillAttribute`, `fillOpacity`, `gap`,
`minBody`, `allowOverlap`, `sizeAttribute`, `sizeScale`, `sizeTarget`,
`lengthMode`, `sizeRange`, `outline`, `labelDeclutter`, `labelOrientation`.
A data-defined node circle (`node_diameter_attribute`) on a collapsed clade is
drawn just past the wedge's outer edge; `show_node_circles = false` (Controls >
Show node circles) hides every data-defined circle without unsetting the
attribute. A collapsed clade whose root node is named is labeled just past the
wedge tip whenever labels are shown (Controls > Show labels); the section
[Label color, direction, and position](#label-color-direction-and-position)
covers which way it reads. Leaf labels must stay unique, so a single-taxon clade
drawn as a leaf gets a readable name through a `[[branch_rule]]` with a `label`
selector and a `clade_label`, which replaces the leaf's displayed name.

## Label color, direction, and position

`label_color` on a `[[branch_rule]]` sets the text color of every label in the
matched subtree: leaf labels, and the wedge label of any collapsed clade inside
it.

```toml
[[branch_rule]]
clade = "Bacteria"
label_color = "#163e8a"
```

A collapsed clade's label sits just past its wedge tip, beyond any node
circle, and by default reads along the branch that enters the clade, walked
back until at least 12 px of branch are in view so a stub of a final segment
does not turn the label. When
several wedges share a bearing their labels land on each other, which no wedge
length or angle setting can fix.
`collapsed_wedge_label_declutter` (Controls: **Collapsed wedge labels** set to
**Leader lines**) pushes a label that overlaps one already placed further out
along the line of its branch until it clears (along its bearing when that line
is blocked, or under the **Outward** direction), so its leader continues the
branch and crowded labels stack in rings. A pushed label gets a thin leader
line back to its wedge, in the label's own color:

```toml
[view]
collapsed_wedge_label_declutter = true
```

It is off by default (**At wedge tip**) and does nothing to a figure whose
labels already clear each other.

`collapsed_wedge_label_orientation` (Controls: **Collapsed wedge label
direction**) sets which way the label reads; the seat is the wedge tip under
either value. `branch` (default, **Along branch**) turns the text to the
branch that enters the clade, for every clade whose root has a parent, so the
labels of a figure read the way their branches run. `bearing` (**Outward**)
turns it out from the center of the drawing, like a spoke. A declutter push
moves the label along its entering branch under `branch`, and outward along
its bearing when that line is blocked or under `bearing`. A leader joins the
label to where it would have sat. A clade whose root has no
parent reads outward under both.

```toml
[view]
collapsed_wedge_label_orientation = "bearing"
```

`allow_label_overlap = false` (Controls: **Auto-cull overlaps**; view
`allowLabelOverlap`) drops a label that would land on one already drawn. The
culler judges a collapsed clade's label at its decluttered seat, so a pushed
label that clears its neighbors is kept. Culled labels return as the view
zooms in: above zoom 1 labels keep their screen size while the tree grows,
so room opens between them. Default `true`.

```toml
[view]
collapsed_wedge_label_declutter = true
allow_label_overlap = false
```

Text on the far side of the figure turns around so it is never upside down. A
clade sitting where that rule turns over reads against its neighbors.
`label_flip` reverses the choice for one label:

```toml
[[branch_rule]]
clade = "Bdellovibrionota"
label_flip = true
```

Any label can also be dragged. Press on the text and move it; the offset is
stored on that clade as `cladeLabelOffsetX` and `cladeLabelOffsetY`, so it
survives saving the session and appears in exports. Set the same values from
the browser API:

```js
await window.__treeviz.execute('tree.style-clade', {
  stableKey,
  patch: { cladeLabelOffsetX: 18, cladeLabelOffsetY: -6, labelFlip: true }
})
```

`cladeLabelPlacement` sets where a clade annotation sits. In TOML, set
`clade_label_placement` on a `[[branch_rule]]`; it accepts the same values.
**Style clade > Clade annotation** offers `clade` and `node`.

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

`cladeBackgroundPadding` sets the padding of one clade's fitted radial
background (`clade_background_outline = "fitted"`) in pixels. It accepts
nonnegative values. Omit it for automatic padding. It is a clade style field
for sessions and `tree.style-clade`; it has no TOML key.

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

A connection set can draw bowed tapered ribbons or straight constant-width
lines. Set `geometry: 'straight'` on the session connection set; the default is
`ribbon`. Pair-level `color`, `width`, and `opacity` apply to either geometry.

Endpoints use exact, case-sensitive node names. A leaf match takes precedence;
otherwise, an internal-node name must be unique. Hidden, collapsed, ambiguous,
and unbound endpoints are omitted and reported through render diagnostics. See
[Connections](API.md#connections) for the JSON shape and diagnostic codes.

## Legends and attribute names

Attribute encodings (branch color, node-circle color, wedge fill from a
node attribute) carry no legend of their own, and the Controls pickers list
their keys as written in the tree. `[[legend]]` tables add hand-written
legends after the legends derived from tracks, markers, node marks and
connections; they appear in the Legend panel, the in-figure legend and
exports. A legend's `shape` is `square` (default, a swatch list) or `circle`.
Circle entries accept an optional `size`, the circle diameter in pixels
(default 10). `[attribute_labels]` maps a node attribute to the name the pickers and
hover tooltips show, as `Name (key)`. `figure_legend = true` opens the
in-figure legend when the session loads.

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

On the session document the `[[legend]]` tables compile to a top-level
`legends` array of `{ title, shape?, entries: [{ label, color, size? }] }`,
`[attribute_labels]` to a top-level `attributeLabels` map from key to name,
and `figure_legend` to `view.figureLegendVisible`. No command edits `legends`
or `attributeLabels`: set them in the document and load it with
`session.restore`. Use `view.set-figure-legend-placement` to show, hide or move
individual sections. Explicit section settings override the global
`view.set-figure-legend-visibility` and `view.toggle-figure-legend` commands.

Session JSON also accepts a continuous scale legend with
`kind: 'continuous-scale'`, `title`, `axisLabel`, `colors`, `domain`, `sizeRange`, `transform`, `ticks`, and optional
`scale`, `orientation`, and `secondaryAxis`. `orientation` is `vertical` by default. A horizontal
ramp runs from low to high left-to-right, with the primary ticks and axis label
upright below it. The optional `secondaryAxis` (`axisLabel`, `domain`,
`transform`, `ticks`) is drawn upright above it. The size
range is nondecreasing and must have a positive maximum; equal positive values
draw a rectangular ramp. `scale` defaults to `1` and accepts finite values from
`0.1` to `4`; it scales the ramp, spacing, strokes, axes, ticks, and text. See
[Browser API](API.md#continuous-attribute-legends) for the session shape and
validation rules. TOML `[[legend]]` supports square and circle legends only,
not continuous scales.

## Conditional style rules

Use conditional style rules when metadata values need thresholds, bins, or
category logic instead of exact visual values. Rules are ordered; later rules
win for the same node or branch target.

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

Rendered targets are `branch-color`, `branch-width`, `node-color`, `node-size`,
`internal-marker-color`, `internal-marker-size`, `label-color`,
`label-weight`, and `label-visibility`. `symbol`, `wedge`, and
`track-bar-color` are saved in sessions and resolved for compact track
workflows; compact track display itself is controlled by `displayMode` on the
track.
