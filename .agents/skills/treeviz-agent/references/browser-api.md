# TreeViz Browser API

Use `window.__treeviz` when TreeViz is opened with `?api=1`.

```text
https://treeviz.newlineages.com/?api=1
```

For render-only automation:

```text
https://treeviz.newlineages.com/?mode=headless&api=1
```

## Core Methods

- `version()`: return app and session-version information.
- `onReady(cb)`: run a callback when the current render state is ready.
- `onChange(cb)`: subscribe to state changes.
- `getSession()`: return the current session or `null`.
- `commands()`: return command descriptors and argument schemas.
- `execute(id, args)`: run a command.
- `getDiagnostics()`: return parse, binding, edit, and render diagnostics.
- `planMetadataImport(source, format, prompt?)`: infer row-key binding and track suggestions.
- `analyzeSessionMetadata(prompt?)`: plan tracks for an existing metadata table.
- `applyTrackRecommendations(recommendations)`: add planner-recommended tracks.
- `resolveClade(query)`: resolve a clade by leaf names or metadata predicates.
- `getLayoutMetrics()`: return render metrics such as clipping and collisions.
- `exportSvg()`: return the current figure as SVG text.

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

const plan = api.planMetadataImport(metadata, 'tsv', 'color by group, show value as bars')
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

## Important Commands

### Session

- `session.import-tree`
- `session.import-metadata`
- `session.rebind`
- `session.restore`
- `session.save`

### Tracks

- `track.add`
- `track.update`
- `track.remove`
- `track.reorder`

Supported track kinds are `color-strip`, `gradient`, `heatmap`, `bar`, `text`,
and `binary-dots`.

### View And Layout

- `view.set-layout`
- `view.set-branch-scale`
- `view.set-leaf-spacing`
- `view.set-metadata-scale`
- `view.set-metadata-gap`
- `view.set-metadata-row-scale`
- `view.set-label-font-size`
- `view.set-label-font-family`
- `view.set-tip-alignment`
- `view.toggle-label-overlap`
- `view.set-branch-colour-attribute`
- `view.set-show-support`
- `view.set-internal-node-marker`
- `view.set-tree-style-attributes`
- `view.set-pretty-terminal-branches`
- `view.set-scale-bar-position`
- `view.set-figure-legend-visibility`
- `view.set-figure-legend-section`
- `view.set-figure-legend-placement`
- `view.set-figure-legend-title`
- `view.set-figure-legend-item-label`
- `view.set-panel-position`

### Tree

- `tree.style-clade`
- `tree.reset-clade-style`
- `tree.collapse-clade`
- `tree.expand-clade`
- `tree.hide-clade`
- `tree.unhide-clade`
- `tree.rotate-clade`
- `tree.reroot`
- `tree.reroot-at-outgroup`
- `tree.midpoint-reroot`
- `tree.prune-clade`
- `tree.extract-subtree`
- `tree.ladderize`
- `tree.sort-by-branch-length`
- `tree.collapse-by-support`

### Export

- `export.newick`
- `export.nexus`
- `export.leaf-names`
- `export.metadata-tsv`

Use `session.save` for a full `.treeviz.json` session.

## Clade Styling

Resolve clades by metadata or leaf names, then style by stable key:

```js
const result = api.resolveClade({
  kind: 'metadata',
  predicates: [{ columnKey: 'group', op: 'equals', value: 'alpha' }]
})

if (result?.exact && result.mrcaStableKey) {
  await api.execute('tree.style-clade', {
    stableKey: result.mrcaStableKey,
    patch: {
      color: '#2563eb',
      label: 'alpha',
      cladeLabelColor: '#2563eb',
      cladeLabelBold: true,
      cladeBackground: 'rgba(37, 99, 235, 0.12)'
    }
  })
}
```

## Support Markers

Numeric internal-node labels in Newick are parsed as support values.

```js
await api.execute('view.set-show-support', { visible: true })
await api.execute('view.set-internal-node-marker', {
  attribute: 'support',
  encoding: 'shade',
  color: '#0f766e'
})
```

## Exact Node And Branch Styling

Use exact style attributes when metadata or tree node comments already contain
visual values. Terminal leaves can read values from bound metadata rows;
internal nodes require tree node metadata.

```js
await api.execute('view.set-tree-style-attributes', {
  nodeDiameterAttribute: 'node_diameter',
  nodeColorAttribute: 'node_color',
  branchWidthAttribute: 'branch_width',
  branchColorAttribute: 'branch_color'
})

await api.execute('view.set-pretty-terminal-branches', {
  enabled: true
})
```

Pretty terminal branches are view-wide and work in rectangular, circular, and
radial layouts. They preserve each branch's current color and mapped width.

## Layout Pass

```js
await api.execute('view.set-layout', { layout: 'rectangular' })
await api.execute('view.set-metadata-gap', { gap: 0 })
await api.execute('view.set-branch-scale', { scale: 0.18 })
await api.execute('view.set-leaf-spacing', { spacing: 0.8 })
await api.execute('view.set-label-font-size', { size: 11 })

const metrics = api.getLayoutMetrics()
const diagnostics = api.getDiagnostics()
const svg = api.exportSvg()
```

Inspect the exported SVG or a screenshot after the final layout change.
