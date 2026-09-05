# Browser API

TreeViz exposes a typed command surface on `window.__treeviz`. Open the hosted
app with `?api=1`. Use `?mode=headless&api=1` for render-only automation.

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
  palettes(): PaletteRecord[]
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

Underscored properties on `window.__treeviz` are internal integration hooks
and are not stable. External tools should use `commands()`, `execute(...)`,
diagnostics, metadata planning, layout metrics, palettes, and export methods.

`palettes()` returns the curated palette records used by the web app, saved
sessions, and examples. Each record includes `id`, `label`, `role`,
`colors`, `recommendedUse`, `warnings`, `colorblindFriendly`, `source`, and
accepted aliases.

Command mutability has three values:

- `document`: persistent session edit; emits `document.changed` and enters
  autosave/history paths.
- `view`: view-only navigation that does not enter the undo ring (currently
  unused; applying a saved view is a `document` edit, so it can be undone).
- `ephemeral`: transient interaction or export command.

## Session Commands

| Command                   | Args                                                              | Effect                                                  |
| ------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------- |
| `session.import-tree`     | `{ source, name, format?, treeIndex? }`                           | Parse Newick/Nexus and load a new session.              |
| `session.import-metadata` | `{ source, format, rowKeyColumn, flags?, leafIdentifierSource? }` | Parse TSV/CSV metadata and bind it to the current tree. |
| `session.rebind`          | `{ flags?, leafIdentifierSource? }`                               | Rebind the current metadata table.                      |
| `session.restore`         | `{ snapshot, skipAutoApplyDefault? }`                             | Restore a `.treeviz.json` session payload.              |
| `session.save`            | `{}`                                                              | Download the current session as `.treeviz.json`.        |
| `session.import-node-metadata` | `{ tsv, rowKeyColumn? }`                                     | Parse TSV keyed to internal nodes and bind it. Rows key on the internal node label, or on an `mrca_of` column holding `|`-separated leaf names. |

`session.restore` takes the whole document, including the top-level `legends`
(hand-written swatch legends, `[{ title, entries: [{ label, color }] }]`) and
`attributeLabels` (node-meta key to display name). No command edits those two
fields.

## View Commands

| Command                               | Args                                                                                                       | Effect                                                                         |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `view.pan`                            | `{ dx, dy }`                                                                                               | Pan the camera.                                                                |
| `view.zoom`                           | `{ factor, panX?, panY? }`                                                                                 | Zoom the camera.                                                               |
| `view.set-layout`                     | `{ layout, connectors?, branchScale?, branchScaleMode?, leafSpacing?, metadataScale?, metadataGap?, labelFontSize?, allowLabelOverlap? }` | Change layout, circular connector style, and optional density settings. |
| `view.set-scale-bar-position`         | `{ x, y }`                                                                                                 | Move the scale bar.                                                            |
| `view.set-panel-position`             | `{ panel, x, y }`                                                                                          | Move `treeHud`, `viewControls`, `inspector`, `figureLegend`, or `utilityDock`. |
| `view.set-panel-size`                 | `{ panel, width, height }`                                                                                 | Resize `viewControls`, `inspector`, or `utilityDock`.                          |
| `view.toggle-branch-lengths`          | `{ enabled }`                                                                                              | Set phylogram/cladogram branch-length mode.                                    |
| `view.set-branch-scale`               | `{ scale }`                                                                                                | Set branch-depth scale.                                                        |
| `view.set-branch-scale-mode`          | `{ mode: 'auto' \| 'manual' }`                                                                             | Allocate topology width automatically or use `branchScale`.                    |
| `view.set-branch-width-scale`         | `{ scale }`                                                                                                | Set branch width scale.                                                        |
| `view.set-leaf-spacing`               | `{ spacing }`                                                                                              | Set leaf row spacing.                                                          |
| `view.set-auto-collapse-threshold`    | `{ threshold }`                                                                                            | Set the automatic collapse threshold.                                          |
| `view.set-metadata-scale`             | `{ scale }`                                                                                                | Set metadata track width scale.                                                |
| `view.set-metadata-gap`               | `{ gap }`                                                                                                  | Set gap between metadata tracks.                                               |
| `view.set-metadata-row-scale`         | `{ scale }`                                                                                                | Set metadata row height scale.                                                 |
| `view.set-label-font-size`            | `{ size }`                                                                                                 | Set label font size.                                                           |
| `view.set-label-font-family`          | `{ family }`                                                                                               | Set label font family.                                                         |
| `view.set-clade-annotation-font-size` | `{ size }`                                                                                                 | Set font size for all clade annotation labels.                                 |
| `view.set-tip-alignment`              | `{ alignment: 'tip' \| 'label' }`                                                                          | Set rectangular label alignment.                                               |
| `view.set-branch-colour-attribute`    | `{ attribute: string \| null }`                                                                            | Color branches by a numeric metadata column or disable the mapping.            |
| `view.set-internal-node-marker`       | `{ attribute?, encoding?, color?, categories? }`                                                           | Map support or internal-node metadata to split markers.                        |
| `view.set-tree-style-attributes`      | `{ nodeDiameterAttribute?, nodeColorAttribute?, branchWidthAttribute?, branchColorAttribute? }`            | Map exact node-circle and branch style values to data attributes.              |
| `view.set-pretty-terminal-branches`   | `{ enabled }`                                                                                              | Decorate branches entering terminal leaves.                                    |
| `view.set-conditional-style-rules`    | `{ rules }`                                                                                                | Replace ordered metadata-driven style rules.                                   |
| `view.set-collapsed-wedge-options`    | `{ shape?, fill?, fillAttribute?, fillOpacity?, gap?, minBody?, allowOverlap?, sizeAttribute?, sizeScale?, sizeTarget?, sizeRange?, outline?, labelDeclutter?, labelOrientation? }`         | Shape, fill, spacing, labels and data sizing for collapsed clade wedges, plus the clade-background outline. `fillAttribute` names the node-meta colour key the `attribute` fill reads; `null` clears it. `fillOpacity` (0..1) sets the translucency of the `branch` and `attribute` fills. `labelDeclutter` pushes crowded wedge labels outward on leader lines instead of seating them at the wedge tip; `labelOrientation` reads them along the incoming branch (`branch`) or outward from the centre (`bearing`). |
| `view.set-node-circles-visible`       | `{ visible }`                                                                                              | Show or hide all data-defined node circles.                                    |
| `view.toggle-labels`                  | `{}`                                                                                                       | Toggle leaf labels.                                                            |
| `view.toggle-support-labels`          | `{}`                                                                                                       | Toggle support labels.                                                         |
| `view.set-show-support`               | `{ visible }`                                                                                              | Set support-label visibility.                                                  |
| `view.set-highlighted-path`           | `{ path }`                                                                                                 | Highlight a path by stable keys.                                               |
| `view.clear-highlighted-path`         | `{}`                                                                                                       | Clear the highlighted path.                                                    |
| `view.toggle-label-overlap`           | `{}`                                                                                                       | Toggle `allowLabelOverlap` (Controls: **Auto-cull overlaps**).                 |
| `view.toggle-metadata`                | `{}`                                                                                                       | Toggle metadata track visibility.                                              |
| `view.set-metadata-visibility`        | `{ visible }`                                                                                              | Set metadata track visibility.                                                 |
| `view.toggle-figure-legend`           | `{}`                                                                                                       | Toggle the compact in-figure legend overlay.                                   |
| `view.set-figure-legend-visibility`   | `{ visible }`                                                                                              | Set in-figure legend overlay visibility.                                       |
| `view.set-figure-legend-section`      | `{ sectionIndex }`                                                                                         | Display one legend section in the figure; use `null` for all sections.         |
| `view.set-figure-legend-placement`    | `{ sectionKey, visible?, x?, y? }`                                                                         | Set per-section figure legend visibility and position.                         |
| `view.set-figure-legend-title`        | `{ sectionKey, title }`                                                                                    | Rename a displayed figure legend title.                                        |
| `view.set-figure-legend-item-label`   | `{ sectionKey, itemKey, label }`                                                                           | Rename a displayed figure legend item label.                                   |
| `view.reset-controls`                 | `{}`                                                                                                       | Reset density control values.                                                  |
| `view.reset-panel-geometry`           | `{}`                                                                                                       | Reset persisted stage panel geometry.                                          |
| `view.save`                           | `{ name, setAsDefault? }`                                                                                  | Save the current view as a named session view.                                 |
| `view.rename`                         | `{ id, name }`                                                                                             | Rename a saved view.                                                           |
| `view.delete`                         | `{ id }`                                                                                                   | Delete a saved view.                                                           |
| `view.set-default`                    | `{ id: string \| null }`                                                                                   | Set or clear the default saved view.                                           |
| `view.apply`                          | `{ id }`                                                                                                   | Apply a saved view.                                                            |

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
- Tip label styling: `labelColor`, `labelBold`, `labelItalic`,
  `labelFontSize`.
- Clade annotations: `label`, `cladeLabelColor`, `cladeLabelBold`,
  `cladeLabelFontSize`.
- Clade underlay: `cladeBackground`. `cladeLabelBackground` is still accepted
  as a legacy alias.
- Collapsed wedge fill: `wedgeFill`, read from the clade's own entry only.
- Node/leaf markers: `internalDotSize`, `leafShape`,
  `nodeCircleDiameter`, `nodeCircleColor`.

Branch styling applies to the target clade root and its descendants while the
clade remains expanded; collapsing is not required to color the clade. A
`patch.label` on an expanded internal node renders a clade-annotation label in
rectangular, circular, and radial layouts. If the same clade is collapsed,
TreeViz uses that label text for the collapsed wedge label. `cladeBackground`
draws a translucent region from the clade root to the descendant tips: a band in
rectangular layout, a sector in circular layout, and a hull around the clade's
tips in radial layout, which has no centre to sweep a sector about. The drawn
region is a click target: left-click selects the clade and tints the region,
right-click opens the clade menu, where Style > Clade underlay recolours it. A
hand-set `color` wins over `branchColorAttribute` and rule colours on the clade
and its descendants, wedge outline included; Reset clade style brings the data
colour back. Clade-annotation
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
pixels. Color values are used as CSS color strings.

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

await api.execute('view.set-tree-style-attributes', {
  nodeColorAttribute: null,
  branchColorAttribute: null
})
```

The older `view.set-branch-colour-attribute` command remains for numeric branch
gradients derived from a metadata column. Exact branch color values from
`view.set-tree-style-attributes` take precedence when both mappings are active.

Use `view.set-pretty-terminal-branches` to thicken and cap only the branch
stubs entering terminal leaves. It works in rectangular, circular, and radial
layouts and preserves each branch's current color and mapped width.

```js
await api.execute('view.set-pretty-terminal-branches', { enabled: true })
```

Use `view.set-conditional-style-rules` for threshold, category, missing-value,
boolean, text, regex, quantile, or rank styling. Source values resolve like
exact styling attributes: `support`, `meta:<key>`, tree node metadata, then
bound leaf metadata rows. Later rules win for the same target.

Rendered targets are `branch-color`, `branch-width`, `node-color`,
`node-size`, `internal-marker-color`, `internal-marker-size`, `label-color`,
`label-weight`, and `label-visibility`. The same rule model also persists
`symbol`, `wedge`, and `track-bar-color` outputs for compact track rendering
workflows.

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
      id: 'host-symbol',
      source: 'host',
      condition: { kind: 'exact', value: 'soil' },
      target: 'symbol',
      value: { shape: 'diamond', color: '#7b3294', size: 9, label: 'Soil host' }
    }
  ]
})

const activeRules = api.getSession().view.conditionalStyleRules
```

In the webapp, open **Controls** to select exact node-circle diameter/color and
branch width/color attributes. Right-click a clade and choose **Style clade**
for clade branch color, line width, dash pattern, label color, label size, and
clade annotation styling; on a collapsed wedge the same popover carries the
wedge outline color and **Wedge fill**. The popover names the clade it styles
and is dragged by that title. Open the **Inspector** on a single leaf or internal
node to edit branch color/width and direct node-circle diameter/color without
writing an API call.

See [Tree styling](STYLING.md) for metadata and browser examples.

## Track Commands

| Command         | Args                                  | Effect                 |
| --------------- | ------------------------------------- | ---------------------- |
| `track.add`     | `{ kind, columnKey, insertAtIndex? }` | Add a metadata track.  |
| `track.remove`  | `{ trackId }`                         | Remove a track.        |
| `track.update`  | `{ trackId, patch }`                  | Update a track config. |
| `track.reorder` | `{ order }`                           | Reorder tracks by id.  |

Supported track kinds are `color-strip`, `gradient`, `heatmap`, `bar`,
`stacked-bar`, `text`, and `binary-dots`. Use `stacked-bar` for composition per
tip: it takes `columnKeys` and splits one bar per leaf into a segment per
column, with `normalize: true` rescaling each row to fill the track.

### Connections

Connections draw tip-to-tip links for horizontal transfer, recombination,
host-parasite pairs, and gene duplication. They are stored on the session as
`connections: [{ id, title, visible, pairs }]`, where each pair is
`{ from, to, label?, color?, width?, opacity? }` naming two leaves. Connection
TSV files may include a `label` column. The figure legend groups pairs by color.
It names each group with the first non-empty label for that color, or with the
color value when no label is present.

Each link is a quadratic curve. Its control point lies on the left-hand
`(-dy, dx)` perpendicular from source to target, and its offset scales with the
chord length. Short links use a 3 px minimum sagitta. Reciprocal links bow to
opposite sides of their shared chord.

For `#rgb` and `#rrggbb` colors, opacity below 1 is encoded as `rgba(...)`; the
default opacity is 0.45. Other color syntaxes pass through unchanged. The layer
is named `connections`, so an export carries `data-tv-layer="connections"`.

An endpoint that matches no leaf produces a diagnostic naming it and the pair is
not drawn. A pair whose endpoints resolve to the same leaf produces a diagnostic
and is not drawn. An endpoint inside a collapsed or hidden clade drops its curve
with a diagnostic rather than drawing to a stale position.

### Node Marks

Marks drawn at internal nodes rather than in the metadata band. They read from
`session.import-node-metadata`, not from the leaf binding.

| Command            | Args                                              | Effect                          |
| ------------------ | ------------------------------------------------- | ------------------------------- |
| `nodemark.add`     | `{ kind: 'pie', columnKeys, style?, palette?, sizeBy?, maxRadius? }` | Add a node mark; `style` is `pie` (default), `donut`, or `bar`. |
| `nodemark.remove`  | `{ index }`                                       | Remove a node mark.             |
| `nodemark.update`  | `{ index, patch }`                                | Update a node mark.             |

Slice angles come from each column's share of its row total. A node whose
columns are all zero or missing draws nothing rather than an empty circle. When
an edit destroys a clade, its mark is dropped with a diagnostic rather than
reattached to a different clade.

For `bar` tracks, `track.update` patches may include `showAxis`,
`axisPosition: "top" | "bottom"`, `showHelperLines`,
`helperLineStyle: "solid" | "dashed"`, `helperLineColor`, and
`helperLineWidth`. Helper lines use the bar-axis tick positions and extend
through the plotted rows in rectangular layout.

`color-strip` tracks can be rendered as compact symbols or wedges by patching
`displayMode: "symbol" | "wedge"` and, for symbols, `symbolShape`.
Supported symbol shapes are `circle`, `square`, `triangle`, `diamond`, `plus`,
and `dash`.

```js
await api.execute('track.update', {
  trackId: 'track:host',
  patch: { displayMode: 'wedge', width: 16 }
})
```

`bar` tracks can keep the normal bar display or use compact interval bins with
`displayMode: "symbol" | "wedge"`. Use `bins` for explicit intervals or
`autoBins` plus a sequential/diverging/neutral `palette` for automatic equal
intervals. Manual bin fields are `label`, `color`, optional `min`/`max`,
optional `minInclusive`/`maxInclusive`, and optional per-bin `shape`.

```js
await api.execute('track.update', {
  trackId: 'track:support',
  patch: {
    displayMode: 'symbol',
    width: 18,
    symbolShape: 'circle',
    bins: [
      { label: 'Low support', max: 60, color: '#d7191c', shape: 'dash' },
      { label: 'High support', min: 90, max: 100, maxInclusive: true, color: '#1a9641' }
    ]
  }
})
```

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
| `view.search`            | `{ query }`               | Match leaf names, leaf labels and collapsed-clade labels; a hit inside a collapsed clade resolves to the wedge. Hits are stable keys in `view.searchHits`. |

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
changes. `getLayoutMetrics()` counts `labelsVisible`, `labelsCulled`,
`labelCollisions` and `labelsClipped` at the current camera. Labels hold their
screen size above zoom 1, so to judge legibility at a target zoom call
`view.zoom`, wait for the next render, and read the metrics again. Capture a
screenshot or exported PNG before calling visual changes complete.

Radial figures with collapsed wedges add `wedgeOverlapPairs`, pairs of wedge
fills that intersect, and `wedgeBranchCrossings`, branches of other lineages
that run through a wedge, both measured on the drawn polygons. Either above
zero puts `metrics.wedge.overlap` in `warnings`. Both fields are absent when
the figure draws no such wedge.

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
