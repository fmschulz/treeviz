# TreeViz Browser API

Use these methods from `window.__treeviz` when TreeViz is opened with `?api=1`.

For procedural metadata/clade guidance, read `session-workflows.md`.
For layout and screenshot QA loops, read `render-qa.md`.

## Launching The Bundled App

The skill ships with a precompiled TreeViz app archive. Launch it from the repo
root with:

```bash
bun .agents/skills/treeviz-agent/scripts/launch-treeviz-app.ts --port 5174
```

Open a session file directly:

```bash
bun .agents/skills/treeviz-agent/scripts/launch-treeviz-app.ts \
  --session path/to/session.treeviz.json \
  --port 5174
```

The launcher extracts `assets/treeviz-app.tar.gz` into the user cache, serves it
over `127.0.0.1`, and prints the `?api=1` URL. Pass `--headless` to add
`mode=headless`, or `--no-open` to avoid opening the browser automatically.

## Core methods

### `execute(id, args)`

Runs a command through the canonical command registry.

Important commands for metadata workflows:

- `session.import-tree`
- `session.import-metadata`
- `session.rebind`
- `session.save`
- `track.add`
- `track.update`
- `track.remove`

### `planMetadataImport(source, format, prompt?)`

Returns a `MetadataAssistantPlan | null`.

Use this before importing metadata. It:

- scores likely row-key columns
- evaluates leaf label vs leaf metadata identifiers
- tries stronger normalization settings
- reports consistency checks
- recommends tracks from the natural-language prompt

Example:

```js
const plan = window.__treeviz.planMetadataImport(
  metadataText,
  'tsv',
  'color by habitat, show abundance as bars, label leaves with host'
)
```

### `analyzeSessionMetadata(prompt?)`

Returns a `MetadataAssistantPlan | null` for the current loaded session.

Use this when metadata is already imported and you want to audit or optimize the session.

### `applyTrackRecommendations(recommendations)`

Applies the planner's recommended tracks sequentially.

It:

- adds tracks through `track.add`
- applies extra patches through `track.update`
- skips duplicate recommendations where possible

Example:

```js
const plan = window.__treeviz.analyzeSessionMetadata('show abundance as bars')
if (plan) {
  await window.__treeviz.applyTrackRecommendations(plan.recommendedTracks)
}
```

### `getLayoutMetrics()`

Returns the latest render metrics, or `null` before the first frame.

Use this before and after layout tuning. Important fields:

- `labelsClipped`
- `labelCollisions`
- `trackDensity`
- `averageBranchPx`
- `warnings`

### `resolveClade(query)`

Returns a `CladeResolutionResult | null`.

Use this when the user asks for a clade by:

- leaf names
- metadata predicates such as `phylum = Proteobacteria`
- combinations of metadata predicates

It reports:

- the matched leaf keys
- the MRCA stable key
- whether the match is an exact monophyletic clade
- any extra leaves pulled in by the MRCA
- unbound metadata rows or unresolved leaf names

## Recommended agent sequence

```js
await window.__treeviz.execute('session.import-tree', {
  source: treeText,
  name: 'tree.nwk',
  format: 'newick'
})

const plan = window.__treeviz.planMetadataImport(metadataText, 'tsv', userGoal)

if (!plan) throw new Error('metadata planning failed')

await window.__treeviz.execute('session.import-metadata', {
  source: metadataText,
  format: 'tsv',
  rowKeyColumn: plan.suggestedBinding.rowKeyColumn,
  flags: plan.suggestedBinding.flags,
  leafIdentifierSource: plan.suggestedBinding.leafIdentifierSource
})

await window.__treeviz.applyTrackRecommendations(plan.recommendedTracks)

const diagnostics = window.__treeviz.getDiagnostics()
const session = window.__treeviz.getSession()
const metrics = window.__treeviz.getLayoutMetrics()
```

## Example: resolve a clade from metadata

```js
const result = window.__treeviz.resolveClade({
  kind: 'metadata',
  predicates: [{ columnKey: 'phylum', op: 'equals', value: 'Proteobacteria' }]
})

if (result?.exact && result.mrcaStableKey) {
  await window.__treeviz.execute('tree.style-clade', {
    stableKey: result.mrcaStableKey,
    patch: {
      color: '#2563eb',
      label: 'Proteobacteria',
      cladeLabelColor: '#2563eb',
      cladeLabelBold: true,
      cladeBackground: 'rgba(37, 99, 235, 0.12)'
    }
  })
}
```

`tree.style-clade` colors the target clade root and descendant branches while
the clade remains expanded. `patch.label` renders an expanded internal clade
annotation in rectangular, circular, and radial layouts; collapsed clades reuse
the same label text on the collapsed wedge. `patch.cladeBackground` fills the
subtree region from the selected ancestor through the terminal descendants.
Clade annotation labels reserve white backing before metadata tracks: a measured
column in rectangular layout and a measured radial lane in circular/radial
layouts. The reserved space follows `patch.label` and `cladeLabelFontSize`.

## Example: show bootstrap support

```js
await window.__treeviz.execute('view.set-show-support', { visible: true })

await window.__treeviz.execute('view.set-internal-node-marker', {
  attribute: 'support',
  encoding: 'shade'
})
```

## Example: resolve a clade from leaf names

```js
const result = window.__treeviz.resolveClade({
  kind: 'leafNames',
  leafNames: ['Escherichia coli', 'Salmonella enterica']
})
```

## Useful commands for agent control

### Metadata and tracks

- `session.import-metadata`
- `session.rebind`
- `track.add`
- `track.update`
- `track.remove`
- `track.reorder`

Bar track patches can set `showAxis`, `axisPosition`, `showHelperLines`,
`helperLineStyle`, `helperLineColor`, and `helperLineWidth`.

### View and layout

- `view.set-layout`
- `view.set-branch-scale`
- `view.set-leaf-spacing`
- `view.set-metadata-gap`
- `view.set-metadata-row-scale`
- `view.toggle-label-overlap`
- `view.set-label-font-size`
- `view.set-clade-annotation-font-size`
- `view.set-tip-alignment`
- `view.set-branch-colour-attribute`
- `view.set-internal-node-marker`
- `view.set-show-support`
- `view.set-scale-bar-position`
- `view.toggle-figure-legend`
- `view.set-figure-legend-visibility`
- `view.set-figure-legend-section`
- `view.set-figure-legend-title`
- `view.set-figure-legend-item-label`
- `view.set-panel-position`

### Tree structure

- `tree.style-clade`
- `tree.collapse-clade`
- `tree.expand-clade`
- `tree.hide-clade`
- `tree.reroot`
- `tree.reroot-at-outgroup`
- `tree.midpoint-reroot`
- `tree.ladderize`
- `tree.sort-by-branch-length`

## Example: iterative layout pass

```js
const api = window.__treeviz

await api.execute('view.set-layout', { layout: 'rectangular' })
await api.execute('view.set-metadata-gap', { gap: 0 })
await api.execute('view.set-branch-scale', { scale: 0.16 })
await api.execute('view.set-leaf-spacing', { spacing: 0.7 })

const metrics1 = api.getLayoutMetrics()
const diagnostics1 = api.getDiagnostics()

if (metrics1 && (metrics1.labelsClipped > 0 || metrics1.labelCollisions > 0)) {
  await api.execute('view.set-label-font-size', { size: 11 })
  await api.execute('view.set-leaf-spacing', { spacing: 0.8 })
}

const metrics2 = api.getLayoutMetrics()
const session2 = api.getSession()
```

Render a PNG after each logical batch rather than waiting until the end.

## Example: styling clades from taxonomy metadata

TreeViz does not guess biological groups for you. The agent should derive the target clade first, then call tree-edit commands with stable keys.

Typical pattern:

1. Import taxonomy metadata with `planMetadataImport(...)` and `session.import-metadata`.
2. Inspect `getSession().metadata` and `getSession().tree`.
3. Resolve the target leaf set from the taxonomy column.
4. Find the relevant stable key for the MRCA/clade.
5. Apply `tree.style-clade`, `tree.collapse-clade`, `tree.reroot`, or track commands.

For numeric metadata mapped onto branches, prefer `view.set-branch-colour-attribute`. For categorical taxonomy, prefer tracks or explicit clade styling.
