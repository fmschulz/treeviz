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
await window.__treeviz.execute('session.restore', { snapshot: sessionDocument })
```

Pass `skipAutoApplyDefault: true` only when the restored snapshot must not apply
its saved default view.

## Core Methods

- `version()`: app and session-version information.
- `onReady(cb)`: run a callback when the current render is ready.
- `onChange(cb)`: subscribe to state changes.
- `getSession()`: current session or `null`.
- `commands()`: command descriptors and argument schemas.
- `palettes()`: palette ids, colors, roles, aliases, and usage notes.
- `execute(id, args)`: run a command.
- `getDiagnostics()`: parse, binding, edit, and render diagnostics.
- `planMetadataImport(source, format, prompt?)`: plan row-key binding and tracks.
- `analyzeSessionMetadata(prompt?)`: plan tracks for loaded metadata.
- `applyTrackRecommendations(recommendations)`: add planned tracks.
- `resolveClade(query)`: resolve leaves or metadata predicates to a stable key.
- `getLayoutMetrics()`: clipping, collision, density, branch, and occupancy metrics.
- `exportSvg()`: current figure as SVG text.

## Import Tree And Metadata

```js
const api = window.__treeviz

await api.execute('session.import-tree', {
  source: '(A,B,(C,D));',
  name: 'tree.nwk',
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

## Tip Connections

Tip-to-tip links live in the session:

```js
{
  connections: [
    {
      id: 'hgt',
      title: 'Transfer',
      visible: true,
      pairs: [
        {
          from: 'A',
          to: 'D',
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
Diagnostics report unresolved endpoints, same-leaf pairs, and endpoints hidden
inside collapsed or hidden clades.

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

Use stable keys for tree edits.

## Layout And Evidence

Keep automatic topology sizing unless fixed geometry is part of the request:

```js
await api.execute('view.set-layout', { layout: 'rectangular' })
await api.execute('view.set-branch-scale-mode', { mode: 'auto' })
await api.execute('view.set-metadata-gap', { gap: 0 })
await api.execute('view.set-leaf-spacing', { spacing: 0.8 })

const diagnostics = api.getDiagnostics()
const metrics = api.getLayoutMetrics()
const svg = api.exportSvg()
```

Calling `view.set-branch-scale` selects manual scale. After the final layout
change, inspect diagnostics, layout metrics, and a screenshot or exported
figure.
