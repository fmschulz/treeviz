# Styling

TreeViz styling is data-first. The hosted browser, `.treeviz.json` sessions,
and `window.__treeviz` use the same palette ids and style fields.
`treeviz-phylo` 0.6.0 bundles the same session schema; sessions written by
0.3.1 are migrated on load.

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
collapsed_wedge_fill = "background"    # or "branch" to fill from the branch colour
collapsed_wedge_gap = 6                # px kept between neighbouring wedges
collapsed_wedge_min_body = 5           # px half-width floor, on top of the stroke
collapsed_wedge_allow_overlap = false  # true keeps crowded wedges as first shaped
collapsed_wedge_size_attribute = "pd"  # size wedges from node metadata instead
collapsed_wedge_size_scale = "log"     # "linear" or "log" (log10)
collapsed_wedge_size_target = "width"  # or "length" to size the wedge's reach
collapsed_wedge_size_range = [10, 80]  # px, outer-edge width or length
clade_background_outline = "hull"      # or "fitted"
```

- `rounded` (default) insets each wedge by half the gap plus half the stroke so
  neighbours stay apart, thickens footprints thinner than the minimum body so a
  two-tip clade reads as a rod rather than a line, rounds the outline, and
  shrinks any pair that would still overlap. `triangle` draws the plain
  triangle from the clade root to the extreme tips; it still gets the minimum
  body where a two-tip clade would otherwise be a hairline.
- `collapsed_wedge_fill` picks the fill. `background` (default) takes the
  nearest enclosing `clade_background`, or the branch colour where there is
  none. `branch` takes the wedge's own branch colour at 28% opacity, which
  tells wedges apart when several sit on one painted clade.
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

The same fields exist on the session view (`collapsedWedgeShape`,
`collapsedWedgeGap`, `collapsedWedgeMinBody`, `collapsedWedgeSizeAttribute`,
`collapsedWedgeSizeScale`, `collapsedWedgeSizeRange`) for `session.restore`.
A data-defined node circle (`node_diameter_attribute`) on a collapsed clade is
drawn just past the wedge's outer edge.

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

## Prompt-To-Figure Recipes

TreeViz does not run a language model in the browser. The expected agent
workflow is: translate a natural-language request into browser commands or
package code; validate the session; render a tight export; then inspect
diagnostics and layout metrics.

### Circular Taxonomy Wedges

Prompt:

> Create a circular tree using a colorblind-safe categorical palette for
> taxonomy, show compact wedge tracks and a diverging trait heatmap, and export
> a tight PNG.

Open the
[hosted bootstrap and taxonomy session](https://treeviz.newlineages.com/?session=%2Fexamples%2Fbootstrap-heatmap-taxonomy%2Fsession.treeviz.json&api=1),
inspect diagnostics and layout metrics, then export PNG or SVG from the app.

Visual intent: circular 100-tip taxonomy tree, bootstrap markers, one compact
phylum wedge ring, and two signed trait heatmap rings.

![Circular taxonomy tree with bootstrap labels, wedge tracks, and diverging heatmap rings.](assets/styling/bootstrap-heatmap-wedges.png)

### Diverging Heatmap And Bar Axis

Prompt:

> Use a blue-red diverging palette centered at zero for signed response scores,
> include a module strip, retain the oxidative-response bar axis, and export a
> compact rectangular figure.

Open the
[hosted differential-expression session](https://treeviz.newlineages.com/?session=%2Fexamples%2Fdifferential-expression%2Fsession.treeviz.json&api=1),
inspect diagnostics and layout metrics, then export PNG or SVG from the app.

Visual intent: a small rectangular tree with a module strip, a dense 30-column
heatmap centered on zero, a quantitative bar axis, and a normalized composition
track.

![Rectangular differential-expression tree with categorical strip, diverging heatmap, and bar axis.](assets/styling/differential-expression-heatmap.png)

### Compact Symbol And Wedge Lanes

Prompt:

> Convert genome size into three symbol bins, render GC content as compact
> wedges, keep the binary marker lanes, and minimize whitespace.

Open the
[hosted genome-symbol session](https://treeviz.newlineages.com/?session=%2Fexamples%2Fgenome-symbol-lanes%2Fsession.treeviz.json&api=1),
inspect diagnostics and layout metrics, then export PNG or SVG from the app.

Visual intent: a compact rectangular example that shows manual bar interval
symbols, automatic bar wedges, categorical strips, binary marker lanes, and a
text fallback lane in one reproducible session.

![Compact genome example with symbol bins, wedge bins, binary marker lanes, and a text marker lane.](assets/styling/genome-symbol-wedge-lanes.png)

### Node And Branch Styling

Prompt:

> Use metadata-defined node circles and branch strokes, draw a turquoise
> ancestor-to-tip gradient plus one warm root-to-tip path, and export a
> manuscript-ready figure.

Open the
[hosted node and branch styling session](https://treeviz.newlineages.com/?session=%2Fexamples%2Fgradient-node-branch-styling%2Fsession.treeviz.json&api=1),
inspect diagnostics and layout metrics, then export PNG or SVG from the app.

Visual intent: exact data-defined node sizes, node colors, branch widths, and
branch colors, with metadata tracks explaining terminal roles.

![Rectangular tree with metadata-defined node circles, branch colors, and tapered branch widths.](assets/styling/gradient-node-branch-styling.png)

## Screenshot Gallery

These screenshots come from the current hosted example sessions. Open the
linked session to inspect the saved state, diagnostics, layout metrics, and
export controls.

| Screenshot | Reproducibility note |
| ---------- | -------------------- |
| ![Differential-expression heatmap](assets/styling/differential-expression-heatmap.png) | [Open session](https://treeviz.newlineages.com/?session=%2Fexamples%2Fdifferential-expression%2Fsession.treeviz.json&api=1). Compact heatmap with a bar axis and composition track. |
| ![Genome symbol and wedge lanes](assets/styling/genome-symbol-wedge-lanes.png) | [Open session](https://treeviz.newlineages.com/?session=%2Fexamples%2Fgenome-symbol-lanes%2Fsession.treeviz.json&api=1). Explicit symbol bins and automatic wedge bins. |
| ![Agent clade playground](assets/styling/agent-clade-playground.png) | [Open session](https://treeviz.newlineages.com/?session=%2Fexamples%2Fagent-clade-playground%2Fsession.treeviz.json&api=1). Clade labels, underlays, symbols, and wedges on a 100-tip tree. |
| ![Bootstrap heatmap wedges](assets/styling/bootstrap-heatmap-wedges.png) | [Open session](https://treeviz.newlineages.com/?session=%2Fexamples%2Fbootstrap-heatmap-taxonomy%2Fsession.treeviz.json&api=1). Circular labels, support marks, wedges, and heatmap rings. |
| ![Gradient node and branch styling](assets/styling/gradient-node-branch-styling.png) | [Open session](https://treeviz.newlineages.com/?session=%2Fexamples%2Fgradient-node-branch-styling%2Fsession.treeviz.json&api=1). Exact node and branch styling with role tracks. |
| ![Large bacterial tree](assets/styling/large-bacterial-tree.png) | [Open session](https://treeviz.newlineages.com/?session=%2Fexamples%2Flarge-bacterial-tree%2Fsession.treeviz.json&api=1). A 6,000-tip stress view with categorical and quantitative rings. |
