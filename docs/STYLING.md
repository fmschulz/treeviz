# Styling

TreeViz styling is data-first. The hosted browser, `.treeviz.json` sessions,
and `window.__treeviz` use the same palette ids and style fields.
Sessions written by earlier releases are migrated on load. Complete figures
built from these settings are on the [Examples](EXAMPLES.md) page.

## Palette Registry

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

## Track Palettes

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

## Compact Track Symbols And Wedges

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

## Exact Node And Branch Styling

Two Controls entries colour branches. **Colour branches by** lists both the
numeric metadata columns, which map onto a colour scale, and any tree-node
metadata key whose values are colours (Newick `[&key=#rrggbb]` comments), which
apply as exact colours; a session that ships several colourings, such as one by
domain and one by a measured quantity, switches between them here. **Exact
styling** exposes the same exact-colour attribute alongside the width and node
circle attributes. Setting one clears the other, so a scale and an exact
colouring never compete.

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

Diameter and branch-width values are pixels. Internal nodes read tree metadata
such as Newick/Nexus annotations; terminal leaves read tree metadata first and
then the bound metadata row. `view.set-tree-style-attributes` sets the four
attribute mappings. Pretty terminal branches are a separate view command.

Branch colours extend upward. An internal node whose children all resolve to
the same colour takes that colour, so a monophyletic group is painted up to and
including the stem of its last common ancestor, and a group that is not
monophyletic is painted up to each of its largest monophyletic parts. A child
without a colour stops the extension. Internal nodes with their own colour value
keep it, and that value counts as the colour of their subtree. On these internal
branches the metadata colour wins over a clade style, as it does on the leaves.

## Layouts

`rectangular`, `circular`, and `radial`. `radial` is the unrooted presentation:
equal-angle placement followed by equal-daylight sweeps, so each branch is drawn
at its own length in its own direction and no point is privileged as the root.

`circular` takes a connector style. `arc` (the default) draws the polar elbow,
an arc across each node's children with a radial spoke out to each one.
`straight` joins parent to child directly and is the layout TreeViz offered as
`radial` through 0.3.1; sessions saved before that release are migrated onto it
automatically.

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

`leaf_spacing` (Controls: **Branch spacing**) sets how much room each leaf
gets. In the rectangular layout it scales the row pitch. The radial layout has
only a full turn to give, so there it shapes the angle split: each child is
weighted by its leaf count raised to this power. Above 1 the wide clades take
more of the turn, which keeps the drawing compact so it renders larger and
crowded regions gain room; below 1 the shares even out and wide clades reach
further, inflating the drawing.

```toml
[view]
layout = "radial"
leaf_spacing = 1.6
```

## Collapsed Clades

Collapse a clade from the browser (`tree.collapse-clade`) or from a config
attribute. With `collapse_attribute`, every non-root internal node whose
tree-node metadata value for that key is truthy (present and not `""`, `"0"`,
or `"false"`) compiles to a collapsed clade. This reaches nodes that name-based
`[[branch_rule]]` selectors cannot, such as many clades sharing one name.

```toml
[view]
collapse_attribute = "collapse"
collapsed_wedge_shape = "rounded"      # or "triangle"
collapsed_wedge_fill = "background"    # "branch", or "attribute" to fill from a node-meta colour key
collapsed_wedge_fill_attribute = "fc"  # node-meta colour key the "attribute" fill reads
collapsed_wedge_fill_opacity = 0.28    # branch/attribute fill opacity; raise it when the fill carries data
collapsed_wedge_gap = 6                # px kept between neighbouring wedges
collapsed_wedge_min_body = 5           # px half-width floor
collapsed_wedge_allow_overlap = false  # true keeps crowded wedges as first shaped
collapsed_wedge_size_attribute = "pd"  # size wedges from node metadata instead
collapsed_wedge_size_scale = "log"     # "linear" or "log" (log10)
collapsed_wedge_size_target = "width"  # or "length" to size the wedge's reach
collapsed_wedge_size_range = [10, 80]  # px, outer-edge width or length
clade_background_outline = "hull"      # or "fitted"
```

- `rounded` (default) insets each wedge by half the gap so neighbours stay
  apart, thickens footprints thinner than the minimum body so a two-tip clade
  reads as a rod rather than a line, rounds the outline, and shrinks any pair
  that would still overlap. `triangle` draws the plain triangle from the clade
  root to the extreme tips; it still gets the minimum body where a two-tip
  clade would otherwise be a hairline. The outline stroke is drawn over the
  body and does not change it: a thicker branch stroke gives a thicker outline
  on the same polygon.
- Gap, minimum body and size range are pixels at full tree scale. When a larger
  label font takes more of the radius, the tree and every wedge, sized or
  footprint-shaped, shrink by the same factor.
- `collapsed_wedge_fill` picks the fill. `background` (default) takes the
  nearest enclosing `clade_background`, or the branch colour where there is
  none. `branch` takes the wedge's own branch colour, translucent, which tells
  wedges apart when several sit on one painted clade. `attribute` reads the
  fill from `collapsed_wedge_fill_attribute`, a node-meta colour key, so the
  fill can encode something other than the outline; a clade without a value
  under that key keeps the `background` fill. `collapsed_wedge_fill_opacity`
  sets the translucency of the `branch` and `attribute` fills (default 0.28, a
  tint); a fill that carries its own data reads better around 0.8.
- `collapsed_wedge_size_attribute` replaces the footprint width with a data
  value: the wedge runs out to its footprint depth and its outer-edge width is
  the value mapped (as-is, or after `log10`) from the range of values across
  the collapsed clades onto `collapsed_wedge_size_range`. Clades without a
  numeric value, and values of zero or below under `log`, keep the footprint
  wedge.
- `collapsed_wedge_size_target` chooses the dimension. `width` (default) puts
  the value in the outer edge. A radial fan constrains that: the angular room
  around each clade belongs to its neighbours, so widths that collide are all
  scaled down by one shared factor, keeping their proportions exact while the
  absolute pixel mapping shrinks. `length` puts the value in the reach from the
  clade root to the base and keeps each clade's own angular slot, so a
  colliding wedge is pulled back on its own and the mapping is left alone.
  `collapsed_wedge_allow_overlap = true` keeps the mapped sizes and permits the
  overlap.
- `clade_background_outline` picks how a `clade_background` is outlined in the
  radial layout. `hull` (default) draws the convex hull of the clade with a
  faint outline. `fitted` draws a soft buffer that follows the branches and
  wedges themselves, with no outline: the buffer is several overlapping shapes
  in one path, and a stroke would draw the seams where they cross.

Each key has a camelCase counterpart on the session view for
`session.restore`: `collapsedWedgeShape`, `collapsedWedgeFill`,
`collapsedWedgeFillAttribute`, `collapsedWedgeFillOpacity`,
`collapsedWedgeGap`, `collapsedWedgeMinBody`, `collapsedWedgeAllowOverlap`,
`collapsedWedgeSizeAttribute`, `collapsedWedgeSizeScale`,
`collapsedWedgeSizeTarget`, `collapsedWedgeSizeRange`,
`cladeBackgroundOutline`, `collapsedWedgeLabelDeclutter`, `allowLabelOverlap`,
and `showNodeCircles`. The command
`view.set-collapsed-wedge-options` patches the same settings under short
names: `shape`, `fill`, `fillAttribute`, `fillOpacity`, `gap`, `minBody`,
`allowOverlap`, `sizeAttribute`, `sizeScale`, `sizeTarget`, `sizeRange`,
`outline`.
A data-defined node circle (`node_diameter_attribute`) on a collapsed clade is
drawn just past the wedge's outer edge; `show_node_circles = false` (Controls >
Show node circles) hides every data-defined circle without unsetting the
attribute. A collapsed clade whose root node is named is labelled just past the
wedge tip, reading outward along the clade's axis, whenever labels are shown
(Controls > Show labels). Leaf labels must stay unique, so a single-taxon clade
drawn as a leaf gets a readable name through a `[[branch_rule]]` with a `label`
selector and a `clade_label`, which replaces the leaf's displayed name.

## Label Colour, Direction, And Position

`label_color` on a `[[branch_rule]]` sets the text colour of every label in the
matched subtree: leaf labels, and the wedge label of any collapsed clade inside
it. One rule per domain colours a whole tree of life.

```toml
[[branch_rule]]
clade = "Bacteria"
label_color = "#163e8a"
```

A collapsed clade's label sits past its own wedge and reads outward from the
centre of the drawing, like a spoke. When several wedges share a bearing their
labels land on each other, which no wedge length or angle setting can fix.
`collapsed_wedge_label_declutter` pushes a label that overlaps one already
placed further out along its own bearing until it clears, so crowded labels
stack in rings. A pushed label gets a thin leader line back to its wedge, in
the label's own colour:

```toml
[view]
collapsed_wedge_label_declutter = true
```

It is off by default and does nothing to a figure whose labels already clear
each other.

`allow_label_overlap = false` (Controls: **Auto-cull overlaps**; view
`allowLabelOverlap`) drops a label that would land on one already drawn. The
culler judges a collapsed clade's label at its decluttered seat, so a pushed
label that clears its neighbours is kept. Culled labels return as the view
zooms in: above zoom 1 labels keep their screen size while the tree grows,
so room opens between them. Default `true`.

```toml
[view]
collapsed_wedge_label_declutter = true
allow_label_overlap = false
```

Text on the far side of the figure turns around so it is never upside down. A
clade sitting where that rule turns over reads against its neighbours.
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

## Legends And Attribute Names

Attribute encodings (branch colour, node-circle colour, wedge fill from a
node-meta key) carry no legend of their own, and the Controls pickers list
their keys as written in the tree. `[[legend]]` tables add hand-written swatch
lists after the legends derived from tracks, markers, node marks and
connections; they appear in the Legend panel, the in-figure legend and
exports. `[attribute_labels]` maps a node-meta key to the name the pickers and
hover tooltips show, as `Name (key)`. `figure_legend = true` opens the
in-figure legend when the session loads.

```toml
[view]
figure_legend = true

[attribute_labels]
vc = "Domain colour"
cc = "Culturedness colour"
fcol = "Isolate colour"

[[legend]]
title = "Domain"
entries = [
  { label = "Bacteria", color = "#1f5fd0" },
  { label = "Archaea", color = "#00ced1" },
  { label = "Eukaryota", color = "#6b8e23" }
]
```

On the session document the `[[legend]]` tables compile to a top-level
`legends` array of `{ title, entries: [{ label, color }] }`,
`[attribute_labels]` to a top-level `attributeLabels` map from key to name,
and `figure_legend` to `view.figureLegendVisible`. No command edits `legends`
or `attributeLabels`: set them in the document and load it with
`session.restore`. `view.set-figure-legend-visibility` and
`view.toggle-figure-legend` control the overlay.

## Conditional Style Rules

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
does (see "Exact Node And Branch Styling").

Rendered targets are `branch-color`, `branch-width`, `node-color`, `node-size`,
`internal-marker-color`, `internal-marker-size`, `label-color`,
`label-weight`, and `label-visibility`. `symbol`, `wedge`, and
`track-bar-color` are saved in sessions and resolved for compact track
workflows; compact track display itself is controlled by `displayMode` on the
track.
