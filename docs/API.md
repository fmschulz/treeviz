# Browser API

TreeViz exposes a typed command surface on `window.__treeviz`. In production
open the app with `?api=1`. Use `?mode=headless&api=1` for render-only
automation.

## Surface

```ts
interface TreevizAPI {
  version(): { app: string; session: 1 }
  onReady(cb: () => void): () => void
  onChange(cb: (evt: ChangeEvent) => void): () => void
  getSession(): SessionDocument | null
  commands(): CommandDescriptor[]
  execute(id: string, args: unknown): Promise<ExecuteResult>
  getDiagnostics(): readonly Diagnostic[]
  parseMetadata(source: string, format: 'tsv' | 'csv', rowKeyColumn: string): MetadataTable
  bindMetadata(tree: TreeDocument, metadata: MetadataTable, flags?: NormalizationFlags): LeafBinding
  planMetadataImport(
    source: string,
    format: 'tsv' | 'csv',
    prompt?: string
  ): MetadataAssistantPlan | null
  analyzeSessionMetadata(prompt?: string): MetadataAssistantPlan | null
  resolveClade(query: CladeResolutionQuery): CladeResolutionResult | null
  applyTrackRecommendations(
    recommendations: MetadataTrackRecommendation[]
  ): Promise<Array<{ recommendation: MetadataTrackRecommendation; result: ExecuteResult }>>
  getLayoutMetrics(): LayoutMetrics | null
  exportSvg(): string
  history: {
    depth(): number
    pointer(): number
    canUndo(): boolean
    canRedo(): boolean
  }
}
```

`commands()` returns the registered command descriptors, including each
command's id, category, mutability, and argument schema. Use it as the source
of truth when building an external tool.

Command mutability has three values:

- `document`: persistent session edit; emits `document.changed` and enters
  autosave/history paths.
- `view`: view navigation/bookkeeping; does not enter the undo ring.
- `ephemeral`: transient interaction or export command.

## Session Commands

| Command                   | Args                                                              | Effect                                                  |
| ------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------- |
| `session.import-tree`     | `{ source, name, format?, treeIndex? }`                           | Parse Newick/Nexus and load a new session.              |
| `session.import-metadata` | `{ source, format, rowKeyColumn, flags?, leafIdentifierSource? }` | Parse TSV/CSV metadata and bind it to the current tree. |
| `session.rebind`          | `{ flags?, leafIdentifierSource? }`                               | Rebind the current metadata table.                      |
| `session.restore`         | `{ snapshot, skipAutoApplyDefault? }`                             | Restore a `.treeviz.json` session payload.              |
| `session.save`            | `{}`                                                              | Download the current session as `.treeviz.json`.        |

## View Commands

| Command                             | Args                                                                                                       | Effect                                                                         |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `view.pan`                          | `{ dx, dy }`                                                                                               | Pan the camera.                                                                |
| `view.zoom`                         | `{ factor, panX?, panY? }`                                                                                 | Zoom the camera.                                                               |
| `view.set-layout`                   | `{ layout, branchScale?, leafSpacing?, metadataScale?, metadataGap?, labelFontSize?, allowLabelOverlap? }` | Change layout and optional density settings.                                   |
| `view.set-scale-bar-position`       | `{ x, y }`                                                                                                 | Move the scale bar.                                                            |
| `view.set-panel-position`           | `{ panel, x, y }`                                                                                          | Move `treeHud`, `viewControls`, `inspector`, `figureLegend`, or `utilityDock`. |
| `view.set-panel-size`               | `{ panel, width, height }`                                                                                 | Resize `viewControls`, `inspector`, or `utilityDock`.                          |
| `view.toggle-branch-lengths`        | `{ enabled }`                                                                                              | Set phylogram/cladogram branch-length mode.                                    |
| `view.set-branch-scale`             | `{ scale }`                                                                                                | Set branch-depth scale.                                                        |
| `view.set-branch-width-scale`       | `{ scale }`                                                                                                | Set branch width scale.                                                        |
| `view.set-leaf-spacing`             | `{ spacing }`                                                                                              | Set leaf row spacing.                                                          |
| `view.set-auto-collapse-threshold`  | `{ threshold }`                                                                                            | Set the automatic collapse threshold.                                          |
| `view.set-metadata-scale`           | `{ scale }`                                                                                                | Set metadata track width scale.                                                |
| `view.set-metadata-gap`             | `{ gap }`                                                                                                  | Set gap between metadata tracks.                                               |
| `view.set-metadata-row-scale`       | `{ scale }`                                                                                                | Set metadata row height scale.                                                 |
| `view.set-label-font-size`          | `{ size }`                                                                                                 | Set label font size.                                                           |
| `view.set-label-font-family`        | `{ family }`                                                                                               | Set label font family.                                                         |
| `view.set-clade-annotation-font-size` | `{ size }`                                                                                               | Set font size for all clade annotation labels.                                 |
| `view.set-tip-alignment`            | `{ alignment: 'tip' \| 'label' }`                                                                          | Set rectangular label alignment.                                               |
| `view.set-branch-colour-attribute`  | `{ attribute: string \| null }`                                                                            | Color branches by a numeric metadata column or disable the mapping.            |
| `view.set-internal-node-marker`     | `{ attribute?, encoding?, color?, categories? }`                                                           | Map support or internal-node metadata to split markers.                        |
| `view.set-tree-style-attributes`    | `{ nodeDiameterAttribute?, nodeColorAttribute?, branchWidthAttribute?, branchColorAttribute? }`             | Map exact node-circle and branch style values to data attributes.              |
| `view.set-pretty-terminal-branches` | `{ enabled }`                                                                                              | Decorate branches entering terminal leaves.                                    |
| `view.toggle-labels`                | `{}`                                                                                                       | Toggle leaf labels.                                                            |
| `view.toggle-support-labels`        | `{}`                                                                                                       | Toggle support labels.                                                         |
| `view.set-show-support`             | `{ visible }`                                                                                              | Set support-label visibility.                                                  |
| `view.set-highlighted-path`         | `{ path }`                                                                                                 | Highlight a path by stable keys.                                               |
| `view.clear-highlighted-path`       | `{}`                                                                                                       | Clear the highlighted path.                                                    |
| `view.toggle-label-overlap`         | `{}`                                                                                                       | Toggle label-overlap allowance.                                                |
| `view.toggle-metadata`              | `{}`                                                                                                       | Toggle metadata track visibility.                                              |
| `view.set-metadata-visibility`      | `{ visible }`                                                                                              | Set metadata track visibility.                                                 |
| `view.toggle-figure-legend`         | `{}`                                                                                                       | Toggle the compact in-figure legend overlay.                                   |
| `view.set-figure-legend-visibility` | `{ visible }`                                                                                              | Set in-figure legend overlay visibility.                                       |
| `view.set-figure-legend-section`    | `{ sectionIndex }`                                                                                         | Display one legend section in the figure; use `null` for all sections.         |
| `view.set-figure-legend-placement`  | `{ sectionKey, visible?, x?, y? }`                                                                         | Set per-section figure legend visibility and position.                         |
| `view.set-figure-legend-title`      | `{ sectionKey, title }`                                                                                    | Rename a displayed figure legend title.                                        |
| `view.set-figure-legend-item-label` | `{ sectionKey, itemKey, label }`                                                                           | Rename a displayed figure legend item label.                                   |
| `view.reset-controls`               | `{}`                                                                                                       | Reset density control values.                                                  |
| `view.reset-panel-geometry`         | `{}`                                                                                                       | Reset persisted stage panel geometry.                                          |
| `view.save`                         | `{ name, setAsDefault? }`                                                                                  | Save the current view as a named session view.                                 |
| `view.rename`                       | `{ id, name }`                                                                                             | Rename a saved view.                                                           |
| `view.delete`                       | `{ id }`                                                                                                   | Delete a saved view.                                                           |
| `view.set-default`                  | `{ id: string \| null }`                                                                                   | Set or clear the default saved view.                                           |
| `view.apply`                        | `{ id }`                                                                                                   | Apply a saved view.                                                            |

## Tree Commands

| Command                                     | Args                             | Effect                                                      |
| ------------------------------------------- | -------------------------------- | ----------------------------------------------------------- |
| `tree.rename-leaf`                          | `{ stableKey, newName }`         | Rename a leaf.                                              |
| `tree.style-clade`                          | `{ stableKey, patch }`           | Apply clade color, line, label, dot, or leaf-shape styling. |
| `tree.reset-clade-style`                    | `{ stableKey }`                  | Clear clade style.                                          |
| `tree.hide-clade` / `tree.unhide-clade`     | `{ stableKey }`                  | Hide or unhide a subtree.                                   |
| `tree.collapse-clade` / `tree.expand-clade` | `{ stableKey }`                  | Collapse or expand a subtree.                               |
| `tree.rotate-clade`                         | `{ stableKey }`                  | Rotate children under a clade.                              |
| `tree.reroot`                               | `{ stableKey }`                  | Reroot at a clade.                                          |
| `tree.reroot-at-outgroup`                   | `{ leafKeys }`                   | Reroot by outgroup leaves.                                  |
| `tree.midpoint-reroot`                      | `{}`                             | Midpoint-reroot the tree.                                   |
| `tree.prune-clade`                          | `{ stableKey }`                  | Remove a clade.                                             |
| `tree.extract-subtree`                      | `{ stableKey }`                  | Return an extracted subtree session and stable-key map.     |
| `tree.ladderize`                            | `{ direction: 'asc' \| 'desc' }` | Ladderize the tree.                                         |
| `tree.sort-by-branch-length`                | `{ direction: 'asc' \| 'desc' }` | Sort clades by branch length.                               |
| `tree.collapse-by-support`                  | `{ threshold }`                  | Collapse clades below a support threshold.                  |

## Clade Annotations And Support

`tree.style-clade` accepts a narrow `patch` object for visual styling:

- Branch styling: `color`, `lineWidth`, `dashPattern`.
- Tip label styling: `labelColor`, `labelBold`, `labelItalic`.
- Clade annotations: `label`, `cladeLabelColor`, `cladeLabelBold`,
  `cladeLabelFontSize`.
- Clade underlay: `cladeBackground`. `cladeLabelBackground` is still accepted
  as a legacy alias.
- Node/leaf markers: `internalDotSize`, `leafShape`.

Branch styling applies to the target clade root and its descendants while the
clade remains expanded; collapsing is not required to color the clade. A
`patch.label` on an expanded internal node renders a clade-annotation label in
rectangular, circular, and radial layouts. If the same clade is collapsed,
TreeViz uses that label text for the collapsed wedge label. `cladeBackground`
draws a translucent region from the clade root to the descendant tips: a band in
rectangular layout and a sector in circular/radial layouts. Clade-annotation
labels reserve readable white backing before metadata tracks: a measured column
in rectangular layout and a measured radial lane in circular/radial layouts. The
reserved space follows the label text and `cladeLabelFontSize`, so tracks start
after the label box as clade labels grow or shrink.

```js
await api.execute('tree.style-clade', {
  stableKey,
  patch: {
    label: 'Imitervirales',
    color: '#4f46e5',
    cladeLabelColor: '#4f46e5',
    cladeLabelBold: true,
    cladeLabelFontSize: 16,
    cladeBackground: 'rgba(79, 70, 229, 0.12)'
  }
})
```

Bootstrap/support values are parsed from numeric internal-node labels in the
tree. `view.set-show-support` and `view.toggle-support-labels` control numeric
support-label visibility. Support labels are independent of split-circle
markers and are skipped for the root node because the root has no incoming
branch to label.

```js
await api.execute('view.set-show-support', { visible: true })

await api.execute('view.set-internal-node-marker', {
  attribute: 'support',
  encoding: 'shade',
  categories: [
    { label: 'Low support (<65)', max: 65, maxInclusive: false, color: '#ffffff' },
    { label: 'Medium support (65-90)', min: 65, max: 90, color: '#9ca3af' }
  ]
})
```

## Data-Defined Node And Branch Styling

Use `view.set-tree-style-attributes` when the tree or metadata table already
contains exact visual values. Diameter and width values are interpreted as
pixels. Color values are CSS color strings.

For internal nodes, attributes are read from tree node metadata such as
Newick/Nexus comments. For terminal nodes, TreeViz reads tree node metadata
first and then falls back to the bound metadata row. Branch style attributes are
keyed by the child node, meaning they style the branch entering that node. The
root node has no incoming branch.

```js
await api.execute('view.set-tree-style-attributes', {
  nodeDiameterAttribute: 'node_diameter',
  nodeColorAttribute: 'node_color',
  branchWidthAttribute: 'branch_width',
  branchColorAttribute: 'branch_color'
})

await api.execute('view.set-pretty-terminal-branches', { enabled: true })
```

Pass `null` for one attribute to clear that mapping without changing the other
mappings:

```js
await api.execute('view.set-tree-style-attributes', {
  nodeColorAttribute: null,
  branchColorAttribute: null
})
```

The pretty terminal branch option works in rectangular, circular, and radial
layouts. It thickens and rounds only the branch stubs entering terminal leaves
and preserves each branch's current color and mapped width.

See [Tree styling](STYLING.md) for TOML, metadata, and Python examples.

## Track Commands

| Command         | Args                                  | Effect                 |
| --------------- | ------------------------------------- | ---------------------- |
| `track.add`     | `{ kind, columnKey, insertAtIndex? }` | Add a metadata track.  |
| `track.remove`  | `{ trackId }`                         | Remove a track.        |
| `track.update`  | `{ trackId, patch }`                  | Update a track config. |
| `track.reorder` | `{ order }`                           | Reorder tracks by id.  |

Supported track kinds are `color-strip`, `gradient`, `heatmap`, `bar`, `text`,
and `binary-dots`.

For `bar` tracks, `track.update` patches may include `showAxis`,
`axisPosition: "top" | "bottom"`, `showHelperLines`,
`helperLineStyle: "solid" | "dashed"`, `helperLineColor`, and
`helperLineWidth`. Helper lines use the bar-axis tick positions and extend
through the plotted rows in rectangular layout.

## Selection And Search Commands

| Command                  | Args                      | Effect                               |
| ------------------------ | ------------------------- | ------------------------------------ |
| `selection.set`          | `{ keys }`                | Replace the selection.               |
| `selection.add`          | `{ keys }`                | Add to the selection.                |
| `selection.remove`       | `{ keys }`                | Remove from the selection.           |
| `selection.clear`        | `{}`                      | Clear the selection.                 |
| `selection.toggle`       | `{ key }`                 | Toggle one stable key.               |
| `selection.select-all`   | `{}`                      | Select visible leaves.               |
| `selection.select-clade` | `{ cladeKey }`            | Select visible leaves under a clade. |
| `selection.style-leaves` | `{ patch }`               | Style the selected leaves.           |
| `view.hover`             | `{ key: string \| null }` | Set or clear hover state.            |
| `view.search`            | `{ query }`               | Search leaf labels.                  |

## History Commands

| Command         | Args | Effect                           |
| --------------- | ---- | -------------------------------- |
| `history.undo`  | `{}` | Undo the previous document edit. |
| `history.redo`  | `{}` | Redo the next document edit.     |
| `history.clear` | `{}` | Clear the undo/redo ring.        |

## Export Commands

| Command               | Args                                     | Effect                                               |
| --------------------- | ---------------------------------------- | ---------------------------------------------------- |
| `export.newick`       | `{}`                                     | Return Newick text.                                  |
| `export.nexus`        | `{ taxaBlock? }`                         | Return Nexus text.                                   |
| `export.leaf-names`   | `{ stableKey, format, includeMetadata }` | Return leaf names under a clade as TXT, CSV, or TSV. |
| `export.metadata-tsv` | `{}`                                     | Return the current metadata table as TSV.            |

Use `session.save` to download a full `.treeviz.json` session. Newick, Nexus,
and metadata exports do not preserve the full visualization state.

## Metadata Import Pattern

```js
const api = window.__treeviz

await api.execute('session.import-tree', {
  source: treeText,
  name: 'tree.nwk',
  format: 'newick'
})

const plan = api.planMetadataImport(metadataText, 'tsv', 'color by phylum')
if (!plan) throw new Error('metadata planning failed')

await api.execute('session.import-metadata', {
  source: metadataText,
  format: 'tsv',
  rowKeyColumn: plan.suggestedBinding.rowKeyColumn,
  flags: plan.suggestedBinding.flags,
  leafIdentifierSource: plan.suggestedBinding.leafIdentifierSource
})

await api.applyTrackRecommendations(plan.recommendedTracks)
```

See [`docs/METADATA.md`](METADATA.md) for the metadata table format.

## Layout QA Pattern

```js
const api = window.__treeviz

await api.execute('view.set-layout', { layout: 'rectangular' })
await api.execute('view.set-metadata-gap', { gap: 0 })
await api.execute('view.set-branch-scale', { scale: 0.7 })

const metrics = api.getLayoutMetrics()
const diagnostics = api.getDiagnostics()
```

Use `getLayoutMetrics()` and `getDiagnostics()` after each logical batch of
changes. Capture a screenshot or exported PNG before calling visual changes
complete.

## Diagnostics

`getDiagnostics()` returns structured diagnostics:

```ts
interface Diagnostic {
  level: 'info' | 'warning' | 'error'
  source: 'parse' | 'bind' | 'edit' | 'render' | 'export' | 'session' | 'autosave' | 'import'
  code: string
  message: string
  context: Record<string, unknown>
  timestamp: number
}
```

Common codes include `parse.too-deep`, `parse.unterminated`,
`parse.tree-index-out-of-range`, `bind.no-matches`, `bind.duplicate-key`,
`import.file-too-large`, `autosave.write-failed`, `autosave.migration-failed`,
`runtime.window-error`, and `runtime.unhandled-rejection`.
