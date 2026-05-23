# Styling

TreeViz styling is data-first. Browser controls, `.treeviz.json` sessions,
TOML configs, Python, R, and `window.__treeviz` should describe the same visual
state with the same palette ids and style fields.

## Palette Registry

The web app ships a small static palette registry. Inspect it from the browser
API:

```js
window.__treeviz.palettes()
```

Each palette record contains:

- `id`: stable palette id accepted by sessions, commands, TOML, Python, and R.
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

TOML:

```toml
[[tracks]]
kind = "color-strip"
column = "phylum"
palette = "okabe-ito"

[[tracks]]
kind = "heatmap"
columns = ["log_fc", "effect"]
palette = "blue-orange"
domain = [-3, 3]
```

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

R:

```r
tracks <- list(
  list(kind = "color_strip", column_key = "phylum", palette = "okabe-ito"),
  list(kind = "heatmap", column_keys = c("log_fc", "effect"), palette = "blue-orange")
)
```

For exact category colors, prefer `category_colors` in TOML or
`categoryColors` in a session/command patch. Exact colors are preserved in
saved sessions and legends.

## Compact Track Symbols And Wedges

Categorical `color-strip` tracks can keep their default strip display or render
each category as compact symbols or wedges:

```toml
[[track]]
kind = "color-strip"
column = "host"
display_mode = "wedge"
width = 16

[[track]]
kind = "color-strip"
column = "quality_tier"
display_mode = "symbol"
symbol_shape = "diamond"
width = 18
```

Numeric `bar` tracks can be converted into interval symbols or wedges. Manual
bins are evaluated in order; `min_inclusive` defaults to true and
`max_inclusive` defaults to false unless set explicitly. `auto_bins` creates
equal-width bins across the track domain.

```toml
[[track]]
kind = "bar"
column = "support"
display_mode = "symbol"
symbol_shape = "circle"
width = 18

[[track.bins]]
label = "Low support"
max = 60
color = "#d7191c"
shape = "dash"

[[track.bins]]
label = "High support"
min = 90
max = 100
max_inclusive = true
color = "#1a9641"
shape = "plus"

[[track]]
kind = "bar"
column = "abundance"
display_mode = "wedge"
auto_bins = 3
palette = "Viridis"
width = 18
```

Browser API fields use camelCase: `displayMode`, `symbolShape`, `autoBins`,
and `maxInclusive`. Supported symbols are `circle`, `square`, `triangle`,
`diamond`, `plus`, and `dash`; legends preserve category labels and interval
labels for symbols and wedges.

## Exact Node And Branch Styling

Use `[view]` in TOML or view fields in wrapper code to map data attributes to
node circles and branch strokes:

```toml
[view]
node_diameter_attribute = "node_diameter"
node_color_attribute = "node_color"
branch_width_attribute = "branch_width"
branch_color_attribute = "branch_color"
pretty_terminal_branches = true
```

The browser equivalent is:

```js
await window.__treeviz.execute('view.set-tree-style-attributes', {
  nodeDiameterAttribute: 'node_diameter',
  nodeColorAttribute: 'node_color',
  branchWidthAttribute: 'branch_width',
  branchColorAttribute: 'branch_color'
})
```

Diameter and branch-width values are pixels. Internal nodes read tree metadata
such as Newick/Nexus annotations; terminal leaves read tree metadata first and
then the bound metadata row.

## Conditional Style Rules

Use conditional style rules when metadata values need thresholds, bins, or
category logic instead of exact visual values. Rules are ordered; later rules
win for the same node or branch target.

```toml
[[style_rule]]
id = "high-abundance-branch"
source = "abundance"
condition = { kind = "interval", min = 10 }
target = "branch-width"
value = 4

[[style_rule]]
id = "soil-labels"
source = "host"
condition = { kind = "exact", value = "soil" }
target = "label-color"
value = "#1d4ed8"

[[style_rule]]
id = "top-abundance-symbol"
source = "abundance"
condition = { kind = "rank", top = 1 }
target = "symbol"
value = { shape = "diamond", color = "#7b3294", size = 9, label = "Top abundance" }
```

Browser API:

```js
await window.__treeviz.execute('view.set-conditional-style-rules', {
  rules: [
    {
      id: 'high-abundance-branch',
      source: 'abundance',
      condition: { kind: 'interval', min: 10 },
      target: 'branch-width',
      value: 4
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

Rendered targets are `branch-color`, `branch-width`, `node-color`, `node-size`,
`internal-marker-color`, `internal-marker-size`, `label-color`,
`label-weight`, and `label-visibility`. `symbol`, `wedge`, and
`track-bar-color` are saved in sessions and resolved for compact track
workflows; compact track display itself is controlled by `displayMode` on the
track.

## Prompt-To-Figure Recipes

TreeViz does not run a language model in the browser. The expected agent
workflow is: translate a natural-language request into TOML, browser commands,
or wrapper code; validate the session; render a tight export; then inspect
diagnostics and layout metrics.

### Circular Taxonomy Wedges

Prompt:

> Create a circular tree using a colorblind-safe categorical palette for
> taxonomy, show compact wedge tracks and a diverging trait heatmap, and export
> a tight PNG.

Deterministic recipe:

```bash
bun run treeviz validate tests/fixtures/datasets/mock-bootstrap-heatmap-taxonomy/treeviz.toml
bun run treeviz render public/examples/bootstrap-heatmap-taxonomy/session.treeviz.json \
  -o docs/assets/styling/bootstrap-heatmap-wedges.png \
  --format png --width 1400 --height 1400 \
  --auto-crop --crop-padding 18
```

Visual intent: circular 100-tip taxonomy tree, bootstrap labels, two compact
categorical wedge rings, and a signed trait heatmap using the shared diverging
palette registry.

![Circular taxonomy tree with bootstrap labels, wedge tracks, and diverging heatmap rings.](assets/styling/bootstrap-heatmap-wedges.png)

### Diverging Heatmap And Bar Axis

Prompt:

> Use a blue-red diverging palette centered at zero for signed response scores,
> include a module strip, retain the oxidative-response bar axis, and export a
> compact rectangular figure.

Deterministic recipe:

```bash
bun run treeviz validate tests/fixtures/datasets/mock-differential-expression/treeviz.toml
bun run treeviz render public/examples/differential-expression/session.treeviz.json \
  -o docs/assets/styling/differential-expression-heatmap.png \
  --format png --width 1600 --height 560 \
  --auto-crop --crop-padding 18
```

Visual intent: a small rectangular tree with a categorical module strip, dense
30-column heatmap centered on zero, and a labeled quantitative bar axis.

![Rectangular differential-expression tree with categorical strip, diverging heatmap, and bar axis.](assets/styling/differential-expression-heatmap.png)

### Compact Symbol And Wedge Lanes

Prompt:

> Convert genome size into three symbol bins, render GC content as compact
> wedges, keep the binary marker lanes, and minimize whitespace.

Deterministic recipe:

```bash
bun run treeviz validate tests/fixtures/datasets/mock-genome-symbol-lanes/treeviz.toml
bun run treeviz render public/examples/genome-symbol-lanes/session.treeviz.json \
  -o docs/assets/styling/genome-symbol-wedge-lanes.png \
  --format png --width 1500 --height 460 \
  --auto-crop --crop-padding 18
```

Visual intent: a compact rectangular example that shows manual bar interval
symbols, automatic bar wedges, categorical strips, binary marker lanes, and a
text fallback lane in one reproducible session.

![Compact genome example with symbol bins, wedge bins, binary marker lanes, and a text marker lane.](assets/styling/genome-symbol-wedge-lanes.png)

### Node And Branch Styling

Prompt:

> Use metadata-defined node circles and branch strokes, draw a turquoise
> ancestor-to-tip gradient plus one warm root-to-tip path, and export a
> manuscript-ready figure.

Deterministic recipe:

```bash
bun run treeviz validate tests/fixtures/datasets/mock-gradient-node-branch-styling/treeviz.toml
bun run treeviz render public/examples/gradient-node-branch-styling/session.treeviz.json \
  -o docs/assets/styling/gradient-node-branch-styling.png \
  --format png --width 1600 --height 560 \
  --auto-crop --crop-padding 18
```

Visual intent: exact data-defined node sizes, node colors, branch widths, and
branch colors, with metadata tracks explaining terminal roles.

![Rectangular tree with metadata-defined node circles, branch colors, and tapered branch widths.](assets/styling/gradient-node-branch-styling.png)

## Screenshot Gallery

All screenshots below are generated from checked-in sessions under
`public/examples/` using `bun run treeviz render --auto-crop --crop-padding 18`.
The source TOML files live under `tests/fixtures/datasets/`.

| Screenshot | Reproducibility note |
| ---------- | -------------------- |
| ![Differential-expression heatmap](assets/styling/differential-expression-heatmap.png) | `public/examples/differential-expression/session.treeviz.json`; 1600 x 560 viewport; selected for compact rectangular heatmap and bar-axis clarity. |
| ![Genome symbol and wedge lanes](assets/styling/genome-symbol-wedge-lanes.png) | `public/examples/genome-symbol-lanes/session.treeviz.json`; 1500 x 460 viewport; selected for explicit bar-to-symbol bins and automatic bar-to-wedge bins. |
| ![Agent clade playground](assets/styling/agent-clade-playground.png) | `public/examples/agent-clade-playground/session.treeviz.json`; 1800 x 1400 viewport; selected for clade labels, underlays, compact symbol bins, and GC wedges on a 100-tip tree. |
| ![Bootstrap heatmap wedges](assets/styling/bootstrap-heatmap-wedges.png) | `public/examples/bootstrap-heatmap-taxonomy/session.treeviz.json`; 1400 x 1400 viewport; selected for circular labels, bootstrap support, categorical wedges, and heatmap rings. |
| ![Gradient node and branch styling](assets/styling/gradient-node-branch-styling.png) | `public/examples/gradient-node-branch-styling/session.treeviz.json`; 1600 x 560 viewport; selected for exact node/branch styling with readable role tracks. |
| ![Large bacterial tree](assets/styling/large-bacterial-tree.png) | `public/examples/large-bacterial-tree/session.treeviz.json`; 1800 x 1400 viewport; selected as a 6000-tip stress view with dense categorical and quantitative metadata rings. |
