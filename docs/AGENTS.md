# Agent Automation

Use the hosted TreeViz API when a script or coding agent needs to build,
inspect, or export a phylogenetic visualization. The API exposes command
schemas, diagnostics, render diagnostics, layout metrics, session state, and
SVG export through `window.__treeviz`.

## Runtime

Open the browser app with the API enabled:

```text
https://treeviz.newlineages.com/?api=1
```

Use headless mode for render-only browser automation:

```text
https://treeviz.newlineages.com/?mode=headless&api=1
```

The hosted [agent API page](https://treeviz.newlineages.com/agent) links the
runtime, command schema, session schema, and example manifest.

## Use the public skill

The installable skill is the complete
[`treeviz-agent` directory](https://github.com/fmschulz/treeviz/tree/main/.agents/skills/treeviz-agent)
in the public repository. It contains the entry file, task-specific references,
and helper scripts. Download or sync the whole directory; `SKILL.md` refers to
the adjacent files.

- [Read `SKILL.md`](https://github.com/fmschulz/treeviz/blob/main/.agents/skills/treeviz-agent/SKILL.md)
- [Open the raw entry file](https://raw.githubusercontent.com/fmschulz/treeviz/main/.agents/skills/treeviz-agent/SKILL.md)
- [Browse the Browser API reference](API.md)
- [Inspect the live command schema](https://treeviz.newlineages.com/treeviz-command-schema.json)
- [Inspect the live session schema](https://treeviz.newlineages.com/treeviz-session.schema.json)
- [List hosted examples](https://treeviz.newlineages.com/examples/manifest.json)

The public skill uses the hosted app. It does not include the browser build or
frontend source.

## Restore the hosted example

```js
const api = window.__treeviz
const response = await fetch('/examples/example-1-mirusviricota/session.treeviz.json')
if (!response.ok) throw new Error(`session request failed: ${response.status}`)
const snapshot = await response.json()
await api.execute('session.restore', { snapshot })
await new Promise(resolve => api.onReady(resolve))
await document.fonts.ready
await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))
```

The session's default saved view applies during restore. Add
`skipAutoApplyDefault: true` only when you need the document's current view.

## Standard sequence

```js
const api = window.__treeviz

await api.execute('session.import-tree', {
  source: '(A,B,(C,D));',
  name: 'example.nwk',
  format: 'newick'
})

const metadataText = [
  'id\tgroup\tvalue',
  'A\talpha\t1.2',
  'B\talpha\t0.8',
  'C\tbeta\t2.1',
  'D\tbeta\t1.6'
].join('\n')

const plan = api.planMetadataImport(metadataText, 'tsv', 'color by group and value')
if (!plan) throw new Error('metadata planning failed')

await api.execute('session.import-metadata', {
  source: metadataText,
  format: 'tsv',
  rowKeyColumn: plan.suggestedBinding.rowKeyColumn,
  flags: plan.suggestedBinding.flags,
  leafIdentifierSource: plan.suggestedBinding.leafIdentifierSource
})

await api.applyTrackRecommendations(plan.recommendedTracks)

await api.execute('view.set-layout', {
  layout: 'circular',
  circularOpeningAngle: 90,
  circularOpeningAutoFit: true,
  circularRotation: 45,
  circularOpeningColor: '#ffffff',
  circularInteriorColor: '#ffffff'
})
await api.execute('view.set-tip-alignment', { alignment: 'label' })

const saved = await api.execute('view.save', { name: 'Circular view' })
if (!saved.ok) throw new Error(saved.error.message)
await api.execute('view.apply', { id: saved.value.id })

await document.fonts.ready
await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))
const diagnostics = api.getDiagnostics()
if (diagnostics.some((item) => item.level === 'error')) {
  throw new Error('TreeViz diagnostics contain errors')
}

const renderDiagnostics = api.getRenderDiagnostics()
const metrics = api.getLayoutMetrics()
const svg = api.exportSvg()
if (!svg.startsWith('<svg')) throw new Error('SVG export failed')
```

Wait for dependent API calls, then let fonts and layout settle before reading
metrics or exporting. `onReady` waits for the first frame after a load; it does
not wait for later edits. Check diagnostics after each batch.

## Practical rules

- Load or restore a session before metadata, tracks, or styling.
- Read `commands()` when an exact command id or argument schema matters.
- Read `palettes()` for palette ids and exact color sets.
- Call `planMetadataImport(...)` before importing metadata from text.
- Use stable keys from the session tree for clade edits.
- Use `categoryColors` when categorical colors must remain exact across uploads.
- Use `displayMode: 'symbol'` or `'wedge'` on color-strip and bar tracks for compact lanes.
- Use `view.set-tree-style-attributes` for data-defined node circles and branch width or color.
- Use `view.set-conditional-style-rules` for metadata thresholds, ranks, missing values, and categories.
- Use `nodemark.add` for pie, donut, or bar marks on bound internal nodes.
- Store tip connections in `session.connections` and resolve endpoint diagnostics before export.
- Keep `branchScaleMode` on `auto` unless the figure requires fixed geometry.
- Use circular opening auto-fit when track names need a clear sector. Set
  `alignment: 'label'` to draw circular tip-to-track guides.
- Save a fitted view with `view.save`; its new id is in `ExecuteResult.value`.
- Put explicit legends in `session.legends` and readable attribute names in `session.attributeLabels` before `session.restore`.
- Use `view.search` to find a taxon or clade by name.
- Save durable work as `.treeviz.json`.
- Read data exports from `ExecuteResult.value`; it contains `content`,
  `filename`, and `mimeType`. `session.save` starts a session download.

## Check the layout

Read `getLayoutMetrics()` after the latest visual change. Start with
`contentOccupancyX`, `contentOccupancyY`, `labelsClipped`, `labelCollisions`,
`labelsVisible`, `labelsCulled`, `trackDensity`, and `p75BranchPx`.

For circular and radial layouts, occupancy is measured against the shorter
viewport side because the figure is round. Metrics describe the current camera.
Labels keep their screen size above zoom 1, so the fitted view and a 2x view can
have different `labelsVisible` and `labelsCulled` counts. Zoom, wait for the
render, and read the metrics again.

Radial figures with collapsed wedges also report `wedgeOverlapPairs` and
`wedgeBranchCrossings`. Either count above zero adds `metrics.wedge.overlap` to
`warnings`.

Inspect the final exported SVG, PNG, or PDF before reporting that a figure is
ready.

## References

- [Browser API](API.md)
- [Metadata](METADATA.md)
- [Tree styling](STYLING.md)
- [Exports](EXPORTS.md)
- [Troubleshooting](TROUBLESHOOTING.md)
