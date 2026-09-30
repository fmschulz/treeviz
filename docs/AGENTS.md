# Agent automation

When a script or coding agent needs to build, inspect, or export a
phylogenetic visualization, use the hosted TreeViz API. Through
`window.__treeviz`, it exposes command schemas, diagnostics, render
diagnostics, layout metrics, and session state, along with SVG and PNG
export.

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

The hosted examples are described in [Examples](EXAMPLES.md).

## Restore the hosted example

```js
const api = window.__treeviz
const response = await fetch('/examples/example-1-mirusviricota/session.treeviz.json')
if (!response.ok) throw new Error(`session request failed: ${response.status}`)
const snapshot = await response.json()
await api.execute('session.restore', { snapshot })
await api.whenSettled()
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

const { metrics, renderDiagnostics } = await api.whenSettled()
const diagnostics = api.getDiagnostics()
if (diagnostics.some((item) => item.level === 'error')) {
  throw new Error('TreeViz diagnostics contain errors')
}

const { dataUrl, width, height } = await api.exportImage({ scale: 2 })
```

Await each command, then `await api.whenSettled()` before reading metrics or
exporting. It resolves once fonts are loaded and the rendered frame matches the
latest edit, and returns the layout metrics and render diagnostics for that
frame. Check diagnostics after each batch. See
[Wait for the render](API.md#wait-for-the-render) and
[Export an image](API.md#export-an-image).

## Practical rules

- Load or restore a session before metadata, tracks, or styling.
- Read `commands()` or `describeCommand(id)` when an exact command id or
  argument schema matters, and `validate(id, args)` to check a call without
  running it.
- Call `planMetadataImport(...)` before importing metadata from text.
- Get stable keys with `findNodes(...)` by name, regex, or metadata value. It
  matches every node; `view.search` matches only leaves and collapsed clades.
- Group related edits with `executeBatch(...)` so a failed step rolls back the
  whole batch.
- `await api.whenSettled()` after each visual change, then read
  `getDiagnostics()` and the returned metrics. Use `getDiagnostics({ since })`
  to see what one batch added.
- Read `describeFigure()` for a compact summary of the current figure.
- Put legends and attribute display names in the session document before
  `session.restore`; no command edits them.
- Export the figure with `exportImage()` after the final layout change and
  inspect it before reporting that the figure is ready.
- Save durable work as `.treeviz.json`.

Command arguments, track options, legends, connections, and node marks are
documented in the [Browser API](API.md) reference. Styling recipes are in
[Tree styling](STYLING.md).

## Check the layout

Read `getLayoutMetrics()` after the latest visual change. Start with
`contentOccupancyX`, `contentOccupancyY`, `labelsClipped`, `labelCollisions`,
`labelsVisible`, `labelsCulled`, `trackDensity`, and `p75BranchPx`.

For circular and radial layouts, occupancy is measured against the shorter
viewport side because the figure is round. Metrics describe the current camera.
Labels keep their screen size above zoom 1, so the fitted view and a 2x view can
have different `labelsVisible` and `labelsCulled` counts. Zoom, await
`whenSettled()`, and read the returned metrics again.

Radial figures with collapsed wedges also report wedge overlap counts; see
[Layout QA pattern](API.md#layout-qa-pattern).

Inspect the final exported SVG, PNG, or PDF before reporting that a figure is
ready.

## References

- [Browser API](API.md)
- [Metadata](METADATA.md)
- [Tree styling](STYLING.md)
- [Exports](EXPORTS.md)
- [Troubleshooting](TROUBLESHOOTING.md)
