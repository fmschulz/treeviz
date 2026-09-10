# TreeViz Browser API

Use `window.__treeviz` when TreeViz is open with `?api=1`.

```text
https://treeviz.newlineages.com/?api=1
https://treeviz.newlineages.com/?mode=headless&api=1
```

## Sources Of Truth

Do not keep a separate full command list in agent notes. Read the live surface:

- `window.__treeviz.commands()` returns command ids and argument schemas.
- `https://treeviz.newlineages.com/treeviz-command-schema.json` is the
  machine-readable command schema.
- `https://fmschulz.github.io/treeviz/API/` documents the API and command
  behavior.
- `window.__treeviz.version()` and `/version.json` identify the running app.

Use the live schema when an exact argument name matters.

Restore a complete session document with:

```js
const response = await fetch('/examples/example-1-mirusviricota/session.treeviz.json')
if (!response.ok) throw new Error(`session request failed: ${response.status}`)
const sessionDocument = await response.json()
await window.__treeviz.execute('session.restore', { snapshot: sessionDocument })
await new Promise(resolve => window.__treeviz.onReady(resolve))
await document.fonts.ready
await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))
```

Pass `skipAutoApplyDefault: true` only when the restored snapshot must not apply
its saved default view. After restore, wait until the camera and
`getLayoutMetrics()` stop changing across several animation frames. A mounted
editor can briefly report its previous viewport.

## Core Methods

- `version()`: app version; its `session` field is a legacy value. Read `getSession().version` or `/version.json` for the session document format.
- `onReady(cb)`: calls `cb` after the first rendered frame for a load, or immediately if that load is ready. For later edits, use the font/frame wait below.
- `onChange(cb)`: subscribe to state changes.
- `getSession()`: current session or `null`.
- `commands()`: command descriptors and argument schemas.
- `palettes()`: palette ids, colors, roles, aliases, and usage notes.
- `execute(id, args)`: run a command.
- `getDiagnostics()`: parse, binding, edit, session, and export diagnostics.
- `getRenderDiagnostics()`: items the last frame could not draw.
- `planMetadataImport(source, format, prompt?)`: plan row-key binding and tracks.
- `analyzeSessionMetadata(prompt?)`: plan tracks for loaded metadata.
- `applyTrackRecommendations(recommendations)`: add planned tracks.
- `resolveClade(query)`: resolve leaves or metadata predicates to a stable key.
- `getLayoutMetrics()`: label visibility, culling, collision and clipping counts, density, branch, and occupancy metrics, at the current camera.
- `exportSvg()`: current figure as SVG text.

## Import Tree And Metadata

```js
const api = window.__treeviz

await api.execute('session.import-tree', {
  source: '(A,B,(C,D));',
  name: 'example.nwk',
  format: 'newick'
})

const metadata = [
  'id\tgroup\tvalue\tpresent',
  'A\talpha\t1.2\tyes',
  'B\talpha\t0.8\tno',
  'C\tbeta\t2.1\tyes',
  'D\tbeta\t1.6\tno'
].join('\n')

const plan = api.planMetadataImport(
  metadata,
  'tsv',
  'color by group and show value as bars'
)
if (!plan) throw new Error('metadata planning failed')

await api.execute('session.import-metadata', {
  source: metadata,
  format: 'tsv',
  rowKeyColumn: plan.suggestedBinding.rowKeyColumn,
  flags: plan.suggestedBinding.flags,
  leafIdentifierSource: plan.suggestedBinding.leafIdentifierSource
})

await api.applyTrackRecommendations(plan.recommendedTracks)
```

Current track kinds are `color-strip`, `gradient`, `heatmap`, `bar`, `text`,
`binary-dots`, and `stacked-bar`.

## Palettes And Compact Tracks

Read palette ids from `palettes()`. Use `categoryColors` when exact category
colors must persist in an uploaded session. Read track ids from
`getSession().tracks` before calling `track.update`.

```js
const palette = api.palettes().find((entry) => entry.id === 'okabe-ito')
if (!palette) throw new Error('palette not found')

await api.execute('track.update', {
  trackId: 'track-host',
  patch: {
    palette: palette.id,
    displayMode: 'wedge',
    categoryColors: {
      soil: '#0072b2',
      water: '#e69f00'
    }
  }
})
```

Color-strip tracks support `strip`, `symbol`, and `wedge` display modes. Bar
tracks support `bar`, `symbol`, and `wedge`; use ordered `bins` or `autoBins`
for numeric intervals.

## Exact And Conditional Styling

Map visual values already present in node or leaf metadata:

```js
await api.execute('view.set-tree-style-attributes', {
  nodeDiameterAttribute: 'node_diameter',
  nodeColorAttribute: 'node_color',
  branchWidthAttribute: 'branch_width',
  branchColorAttribute: 'branch_color'
})

await api.execute('view.set-pretty-terminal-branches', { enabled: true })
```

Branch colours from `branchColorAttribute` and `branch-color` rules extend up to
the MRCA stem of each same-coloured clade and win over clade styles there.

`branchColorAttribute` reads a node-meta key whose values are colours (Newick
`[&key=#rrggbb]` comments) and applies them as exact branch and wedge-outline
colours. `view.set-branch-colour-attribute` maps a numeric metadata-table
column onto a colour scale. Use one at a time: clear the other with
`branchColorAttribute: null` or `{ attribute: null }`.

Apply ordered conditions when the source data holds measurements or classes:

```js
await api.execute('view.set-conditional-style-rules', {
  rules: [
    {
      id: 'high-abundance-branch',
      source: 'abundance',
      condition: { kind: 'interval', min: 10 },
      target: 'branch-width',
      value: 4
    },
    {
      id: 'missing-host-label',
      source: 'host',
      condition: { kind: 'missing' },
      target: 'label-visibility',
      value: false
    }
  ]
})
```

Conditions include `exact`, `interval`, `quantile`, `rank`, `missing`,
`boolean`, `contains`, and `regex`. Read the live command schema for target and
value types.

## Internal Node Marks

Import metadata keyed to named internal nodes with
`session.import-node-metadata`. Add, update, or remove marks with
`nodemark.add`, `nodemark.update`, and `nodemark.remove`.

`nodemark.add` uses `kind: 'pie'`; `style` selects `pie`, `donut`, or `bar`.
`columnKeys` names the component columns, and `palette` selects their colors.
One mark definition applies to every bound internal-node row. Optional `sizeBy`
and `maxRadius` control size.

## Connections

Connections between leaves or named internal nodes live in the session:

```js
{
  connections: [
    {
      id: 'hgt',
      title: 'Transfer',
      visible: true,
      geometry: 'straight',
      pairs: [
        {
          from: 'Archaeal_clade',
          to: 'Bacterial_leaf',
          label: 'putative transfer',
          color: '#0072b2',
          width: 2,
          opacity: 0.45
        }
      ]
    }
  ]
}
```

Add connections to a `.treeviz.json` document, then call
`session.restore` with `{ snapshot: sessionDocument }`.
Names match exactly and case-sensitively. A leaf match takes precedence;
otherwise, an internal-node name must be unique. `geometry` defaults to
`ribbon`, a bowed tapered path. `straight` draws a constant-width line.
Check `connections.ambiguous-endpoint`, `connections.unbound-endpoint`,
`connections.hidden-endpoint`, and `connections.collapsed-endpoint` before
export. `connections.self-link` and `connections.coincident-endpoints` also
omit their pairs.

## Clade Resolution And Styling

Resolve clades from metadata instead of selecting pixels:

```js
const result = api.resolveClade({
  kind: 'metadata',
  predicates: [{ columnKey: 'group', op: 'equals', value: 'alpha' }]
})

if (result?.exact && result.mrcaStableKey) {
  await api.execute('tree.style-clade', {
    stableKey: result.mrcaStableKey,
    patch: {
      color: '#0072b2',
      label: 'alpha',
      cladeLabelColor: '#0072b2',
      cladeLabelBold: true,
      cladeBackground: 'rgba(0, 114, 178, 0.12)'
    }
  })
}
```

Use stable keys for tree edits. A hand-set `patch.color` wins over
`branchColorAttribute` and rule colours on the clade and its descendants; on a
collapsed clade it recolours the wedge outline and `patch.wedgeFill` sets the
wedge fill. The region `patch.cladeBackground` draws is itself a click target:
left-click selects the clade, right-click opens its menu.

Set `patch.cladeBackgroundGradient` or `patch.wedgeFillGradient` to `{ startColor: '#ffffff', endColor: '#8f85b5' }`.
The gradient runs from the clade root toward its descendants and applies only
to that clade. A background gradient needs no solid background. A wedge
gradient overrides the solid fill, mode and mode opacity. Endpoints accept
`#rrggbb` and `rgba(r,g,b,a)`; use the latter for alpha. An explicit `undefined`
removes a gradient through the JavaScript API. Coincident root and descendant extents render as solid `endColor` in Canvas and SVG.

For text centered on a node, set `patch.cladeLabelPlacement: 'node'`. It uses
`patch.label`, `cladeLabelFontSize` (fractional 1–96 px), `cladeLabelColor`,
`cladeLabelBold`, and the offsets. It works on internal and terminal nodes,
stays horizontal, and reserves no outer label lane. Terminal nodes get one
label. Use `view.set-layout` with `{ layout, showScaleBar: false }` to hide the
distance scale without changing branch geometry.

## Collapsed Wedges And Backgrounds

Collapse a clade with `tree.collapse-clade`; the session records it as
`cladeStyles[stableKey].collapsed`. In the radial layout every collapsed clade
draws as a wedge. `view.set-collapsed-wedge-options` applies a partial patch:

```js
await api.execute('view.set-collapsed-wedge-options', {
  shape: 'rounded',      // or 'triangle'
  fill: 'attribute',     // 'background' | 'branch' | 'attribute'
  fillAttribute: 'cc',   // node-meta colour key the 'attribute' fill reads
  fillOpacity: 0.8,      // default 0.28; near 0.8 when the fill carries data
  gap: 6,                // px between neighbouring wedges
  minBody: 5,            // px half-width floor
  allowOverlap: false,
  sizeAttribute: 'pd',   // node-meta numeric key
  sizeScale: 'log',      // or 'linear'
  sizeTarget: 'length',  // or 'width'
  sizeRange: [40, 400],  // px [min, max]
  outline: 'fitted',     // clade-background outline: 'hull' | 'fitted'
  labelDeclutter: true,  // push colliding labels outward on leader lines
  labelOrientation: 'branch' // default; 'bearing' reads out from the centre
})
```

The session view fields are `collapsedWedgeShape`, `collapsedWedgeFill`,
`collapsedWedgeFillAttribute`, `collapsedWedgeFillOpacity`,
`collapsedWedgeGap`, `collapsedWedgeMinBody`, `collapsedWedgeAllowOverlap`,
`collapsedWedgeSizeAttribute`, `collapsedWedgeSizeScale`,
`collapsedWedgeSizeTarget`, `collapsedWedgeSizeRange`, and
`cladeBackgroundOutline`. A `treeviz.toml` uses the snake_case forms plus
`collapse_attribute`, which collapses every internal node whose node-meta value
for that key is truthy.

`sizeTarget: 'length'` puts the value in the wedge's reach from clade root to
base and keeps each clade's angular slot, so one colliding wedge is pulled back
on its own: it gives up length against neighbouring wedges and branches of
other lineages down to its footprint depth, then narrows its base to the
minimum body. What it cannot clear is counted in `getLayoutMetrics()` as
`wedgeOverlapPairs` and `wedgeBranchCrossings`. `sizeTarget: 'width'` puts the
value in the outer edge; colliding widths in a crowded fan are scaled down by
one shared factor. Wedge outlines, and the hover and selection outlines, are
painted inside the fill and capped at 60% of the wedge's inradius, so a thin
wedge keeps a visible fill at any branch width. A wedge keeps `gap` px from
its neighbours and from the centre line of branches of other lineages; the
branch stroke does not move it.

Node circles and labels draw on top of wedges:

```js
await api.execute('view.set-node-circles-visible', { visible: false })
await api.execute('view.toggle-labels')
```

`view.set-node-circles-visible` sets `showNodeCircles` and hides every
data-defined node circle without unsetting the style attributes.
`view.toggle-labels` flips `showLabels`. A collapsed clade whose root node is
named is labelled beyond its wedge tip in radial, and that label follows
`showLabels`. `collapsedWedgeLabelDeclutter: true` pushes colliding labels
outward with leader lines; `collapsedWedgeLabelOrientation` turns each label
to the branch entering its clade (`'branch'`, the default) or out from the
centre (`'bearing'`), with the seat at the wedge tip under both;
`allowLabelOverlap: false` culls the ones that still collide, judged at their
pushed seats. Hovering or selecting a collapsed clade outlines its wedge.

## Legends And Attribute Names

Hand-written legends and picker names live on the session document, not
behind a command. Add them and restore:

```js
const doc = api.getSession()
await api.execute('session.restore', {
  snapshot: {
    ...doc,
    legends: [
      {
        title: 'Domain',
        entries: [
          { label: 'Bacteria', color: '#1f5fd0' },
          { label: 'Archaea', color: '#00ced1' }
        ]
      }
    ],
    attributeLabels: { vc: 'Domain colour' }
  }
})
await api.execute('view.set-figure-legend-placement', { sectionKey: 'custom:0', visible: true })
```

`legends` follow the legends derived from tracks, markers, node marks and
connections in the Legend panel, the in-figure legend and exports. Pickers and
hover tooltips show a labelled key as `Domain colour (vc)`. In a
`treeviz.toml` these are `[[legend]]` tables, `[attribute_labels]`, and
`figure_legend = true` under `[view]`.

Custom legend keys are `custom:0`, `custom:1`, etc. Use
`view.set-figure-legend-placement` with `visible: false` to hide a section
in both the figure and export; pass `x` and `y` together to move it. Explicit
section visibility overrides `view.set-figure-legend-visibility`.

For numeric size/color encodings, session JSON also accepts
`{ kind: 'continuous-scale', title, axisLabel, colors, domain, sizeRange, transform, ticks, scale?, orientation? }`.
`orientation` defaults to `vertical`; `horizontal` runs low-to-high
left-to-right. `sizeRange` must be nondecreasing with a positive maximum, so
equal positive values draw a rectangular ramp. Optional `scale` defaults to
`1`, accepts finite values from `0.1` to `4`, and scales the ramp and text.
The legend describes stored display values; it does not compute them. TOML
legends define swatches only.

Add `secondaryAxis: { axisLabel, domain, transform, ticks }` for a separate
numeric scale. Horizontal primary labels are upright below the ramp and
secondary labels are upright above it; vertical axes are left and right. Each
axis uses its own domain and transform. Domains must increase, square-root
domains must be nonnegative, and ticks must lie inside their own domains.

## Search, Hover And Zoom

```js
await api.execute('view.search', { query: 'Cyanobacteriota' })
const hits = api.getSession().view.searchHits // stable keys
await api.execute('view.hover', { key: hits[0] ?? null })
await api.execute('view.zoom', { factor: 2 })
```

`view.search` matches leaf names, leaf labels and collapsed-clade labels; a hit
inside a collapsed clade resolves to that clade's wedge. Clear it with an empty
query. Above zoom 1 labels, strokes and node marks keep their screen size while
the tree grows, and the label culler re-runs once the camera has been still
for about 150 ms, so read `getLayoutMetrics()` after that: `labelsVisible`,
`labelsCulled`, `labelCollisions` and `labelsClipped` describe the current
camera. `exportSvg()` applies the same screen-size rule, so an SVG taken while
zoomed matches the screen.

## Layout And Evidence

Keep automatic topology sizing unless fixed geometry is part of the request:

```js
await api.execute('view.set-layout', {
  layout: 'circular',
  circularOpeningAngle: 90,
  circularOpeningAutoFit: true,
  circularRotation: 45,
  circularOpeningColor: '#ffffff',
  circularInteriorColor: '#ffffff'
})
await api.execute('view.set-tip-alignment', { alignment: 'label' })
await api.execute('view.set-branch-scale-mode', { mode: 'auto' })
await api.execute('view.set-metadata-gap', { gap: 0 })

await document.fonts.ready
await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))
const diagnostics = api.getDiagnostics()
const renderDiagnostics = api.getRenderDiagnostics()
const metrics = api.getLayoutMetrics()
const svg = api.exportSvg()
```

Calling `view.set-branch-scale` selects manual scale. After the final layout
change, inspect both diagnostic arrays, layout metrics, and a screenshot or
exported figure.

Circular opening arguments are saved in the session and in named views. The
opening angle accepts 0 to 350 degrees, and rotation accepts -180 to 180
degrees. Auto-fit adjusts the opening when track names, visible tracks, ring
widths, or the viewport change. It keeps the label edge fixed and does not
respond to zoom or pan. Opening and interior colors accept `#RRGGBB` or `null`.
In circular layout, `alignment: 'label'` draws guides from tips to the inner
edge of the visible metadata rings; use `'tip'` to turn them off.

`circularAngleAttribute` selects a direct `node.meta` key containing angles in
degrees from 0 through 360. Finite numbers and nonempty numeric strings are
accepted. Missing, Boolean, nonfinite, or out-of-range values use the automatic
angle for that node. Bound metadata-table columns are excluded. Values map into
the current opening and rotation; opening 0 with rotation 90 gives clockwise
angles from the right. Keep values in traversal order for arc connectors and
collapsed spans. Pass `null` to clear the setting. Rectangular and radial
layouts ignore it.

For imported radial positions, set `radialXAttribute` and `radialYAttribute`
through `view.set-layout`. They select direct node metadata, with positive Y
pointing down. Every node needs both values as finite numbers or nonempty
numeric strings. An incomplete key pair, or any missing, Boolean, blank,
nonnumeric, or nonfinite coordinate, uses automatic radial layout and reports
`render.radial-coordinates-invalid`. Imported positions ignore branch lengths
and spacing. Pass both keys as `null`, or set both **Controls > Layout**
selectors to **Automatic**, to clear them. Circular and rectangular layouts
ignore the keys.

Save and reapply an exact view after fitting it:

```js
const saved = await api.execute('view.save', {
  name: 'Example 1',
  setAsDefault: true
})
if (!saved.ok) throw new Error(saved.error.message)
const savedViewId = saved.value.id
await api.execute('view.apply', { id: savedViewId })
```

`view.save` returns the new id in `ExecuteResult.value`. A default view applies
when `session.restore` loads the session unless `skipAutoApplyDefault: true` is
set. The four data export commands return `{ content, filename, mimeType }` in
`ExecuteResult.value`. `session.save` starts a `.treeviz.json` download.
