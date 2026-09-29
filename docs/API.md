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
  commands(): CommandSummary[]
  describeCommand(id: string): CommandDescription
  execute(id: string, args?: unknown): Promise<ExecuteResult>
  executeBatch(steps: BatchStep[], opts?: BatchOptions): Promise<BatchResult>
  validate(id: string, args?: unknown): ValidationResult
  getDiagnostics(opts?: { since?: number }): SequencedDiagnostic[]
  clearDiagnostics(): void
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
  getRenderDiagnostics(): readonly RenderDiagnostic[]
  whenSettled(opts?: { timeoutMs?: number }): Promise<SettleResult>
  exportSvg(): string
  exportImage(opts?: ExportImageOptions): Promise<ExportImageResult>
  findNodes(query: FindNodesQuery): FoundNode[]
  describeFigure(): FigureDescription
  history: {
    depth(): number
    pointer(): number
    canUndo(): boolean
    canRedo(): boolean
  }
}
```

`commands()` returns every registered command as plain JSON: `id`, `label`,
`description`, `category`, `mutability` and `argsSchema`. `argsSchema` is JSON
Schema (draft 2020-12) for the arguments as a caller sends them, so an argument
with a default is optional. Use it as the source of truth when building an
external tool. For tools that do not run the app, the same schemas are served
next to the app as
[`/treeviz-command-schema.json`](https://treeviz.newlineages.com/treeviz-command-schema.json)
(commands) and
[`/treeviz-session.schema.json`](https://treeviz.newlineages.com/treeviz-session.schema.json)
(the `.treeviz.json` document).

`version().session` is a legacy value of `1`. The document format is
`getSession().version`, also published as `schemaVersions.session` in `/version.json`.
`onReady` signals the first rendered frame after a session load. After a
restore or any later edit, call `whenSettled()` before reading metrics or
exporting. See the [agent workflow](AGENTS.md).

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

## Discover a command

`describeCommand(id)` returns one command: `id`, `label`, `description` (one
sentence naming the key arguments), `mutability`, `argsSchema`, and an `example`
argument object when one is published. Every example is checked against the
command's own schema. It throws for an unknown id and suggests close ones.

```js
const api = window.__treeviz
const { description, argsSchema, example } = api.describeCommand('view.set-layout')
// example: { layout: 'circular', circularOpeningAngle: 60, showScaleBar: false }
await api.execute('view.set-layout', example)
```

Stable keys in examples are placeholders. Get real ones from `getSession().tree`
or `findNodes(...)`.

## Running commands

`execute(id, args?)` resolves to an `ExecuteResult`. It does not throw for a
failed command.

```ts
type ExecuteResult =
  | { ok: true; value?: unknown }
  | { ok: false; error: { code: string; message: string; details?: unknown } }
```

Omit `args` for a command that takes none: `execute('history.undo')` is the same
as `execute('history.undo', {})`.

Executions run one at a time, in call order. `Promise.all([execute(a), execute(b)])`
is safe: `b` starts after `a` has finished and sees its changes.

A failed command does not apply its edit. A document command first saves the
current zoom and pan into the session, so that part can change even when the
command fails. `error.code` is one of:

| Code | Meaning | `details` |
| --- | --- | --- |
| `command.unknown` | No command has that id. | `{ suggestions }`: up to five close command ids |
| `command.invalid-args` | `args` do not match the command's schema. | zod `flatten()` output |
| `command.target-not-found` | A stable key, track id, metadata column or saved-view id is not in the current session. | `{ kind, value, suggestions, candidateCount, unknownKeys? }` |
| `command.invalid-target` | The target exists but is the wrong kind, such as an internal node given to `tree.rename-leaf` or `tree.reroot-at-outgroup`. | `{ kind, value, suggestions }`: leaves under the node |
| `command.invalid-patch` | `track.update`: the patch has an unknown key (a typo, or `id`/`kind`) or an invalid value. Nothing in the patch is applied. | `{ trackId, kind, unknownKeys?, suggestions?, issues? }` |
| `command.invalid-order` | `track.reorder`: `order` is not every current track id exactly once. | `{ order, current, unknown, missing, duplicates }` |
| `command.handler-threw` | Any other failure: no session loaded, a parse error, and so on. | not meaningful |

Errors about a value that does not exist name the value and list up to five
close valid alternatives, for example
`no node with stable key "Pan". Did you mean: "19683af7592d" (leaf "Pan")?`.
Stable keys also match node names, track ids match titles, and saved-view ids
match names, so passing the name where the id belongs returns the id.

### validate

`validate(id, args?)` checks a call against the command's args schema without
running it:

```ts
validate(id: string, args?: unknown): {
  ok: boolean
  errors: Array<{ path: string; message: string; expected?: string }>
  didYouMean?: string[] // close command ids, when `id` is not a command
}
```

`path` is dotted into `args` (`patch.color`, `keys[0]`) and empty for the args
object itself. Unrecognized keys of a strict schema are reported one per key.
`validate` does not read the session, so it cannot tell that a well-formed
stable key or track id does not exist; `execute` reports that.

### executeBatch

`executeBatch(steps, opts?)` runs several commands as one unit.

```ts
executeBatch(
  steps: Array<{ id: string; args?: unknown }>,
  opts?: { atomic?: boolean; dryRun?: boolean } // atomic defaults to true
): Promise<{
  ok: boolean // every step that ran succeeded
  rolledBack: boolean // state was restored to what it was before the batch
  results: Array<{
    id: string
    ok: boolean
    value?: unknown
    error?: { code: string; message: string; details?: unknown }
    diagnostics?: Diagnostic[] // pushed by this step
    skipped?: true // dry run only: session.save is not run
  }>
  dryRun?: true
  error?: { code: 'batch.invalid-steps'; message: string } // nothing ran
}>
```

- The batch holds the execution queue for its whole length: no other
  `execute` interleaves, and each step sees the previous step's changes.
- Atomic (default): the first failing step stops the batch. The session, live
  camera, undo history and diagnostics are restored, so a rolled-back batch
  leaves no undo entries and `rolledBack` is `true`. `results` ends at the
  failing step.
- `atomic: false` runs every step, keeps what succeeded, and reports each
  failure in `results`. Nothing is restored.
- `dryRun: true` runs the steps, then always restores, and returns what would
  happen (`rolledBack` is `true`; `ok` says whether a real run would succeed).
  With `atomic` (the default) it stops at the first failure, as a real run would.
  Change events fire while it runs, and `value`s such as the id from `view.save`
  refer to state that no longer exists afterwards. `session.save` is skipped.
- A batch that is kept leaves one undo entry per document-changing step, the
  same as running the steps one by one.
- An effect outside the app, such as the file `session.save` downloads, cannot
  be rolled back.

## Session commands

| Command                   | Args                                                              | Effect                                                  |
| ------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------- |
| `session.import-tree`     | `{ source, name, format?, treeIndex? }`                           | Parse Newick/Nexus and load a new session.              |
| `session.import-metadata` | `{ source, format, rowKeyColumn, flags?, leafIdentifierSource? }` | Parse TSV/CSV metadata and bind it to the current tree. |
| `session.rebind`          | `{ flags?, leafIdentifierSource? }`                               | Rebind the current metadata table.                      |
| `session.restore`         | `{ snapshot, skipAutoApplyDefault? }`                             | Restore a `.treeviz.json` session payload.              |
| `session.save`            | `{}`                                                              | Download the current session as `.treeviz.json`.        |
| `session.import-node-metadata` | `{ tsv, rowKeyColumn? }`                                     | Parse TSV keyed to internal nodes and bind it. Rows key on the internal node label, or on an `mrca_of` column holding `|`-separated leaf names. |

`session.restore` takes the whole document, including top-level `legends` and
`attributeLabels` (node attribute to display name). Legends can be hand-written
swatches (`[{ title, entries: [{ label, color }] }]`) or continuous scales.
No command edits those two fields. An optional `meta.description` string can
record provenance in the saved `.treeviz.json` document.

## View commands

| Command                               | Args                                                                                                       | Effect                                                                         |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `view.pan`                            | `{ dx, dy }`                                                                                               | Pan the camera.                                                                |
| `view.zoom`                           | `{ factor, panX?, panY? }`                                                                                 | Zoom the camera.                                                               |
| `view.set-layout`                     | `{ layout, connectors?, collapsedCladeSpacing?, circularOpeningAngle?, circularOpeningAutoFit?, circularRotation?, circularAngleAttribute?, radialXAttribute?, radialYAttribute?, circularOpeningColor?, circularInteriorColor?, branchScale?, branchScaleMode?, leafSpacing?, metadataScale?, metadataGap?, labelFontSize?, allowLabelOverlap?, showScaleBar? }` | Change layout, collapsed-clade spacing, imported node positions, circular angles and fills, connector style, density settings, and scale visibility. |
| `view.set-scale-bar-position`         | `{ x, y }`                                                                                                 | Move the scale bar.                                                            |
| `view.set-panel-position`             | `{ panel, x, y }`                                                                                          | Move `treeHud`, `viewControls`, `inspector`, `figureLegend`, or `utilityDock`. |
| `view.set-panel-size`                 | `{ panel, width, height }`                                                                                 | Resize `viewControls`, `inspector`, or `utilityDock`.                          |
| `view.toggle-branch-lengths`          | `{ enabled }`                                                                                              | Set phylogram/cladogram branch-length mode.                                    |
| `view.set-branch-scale`               | `{ scale }`                                                                                                | Set branch-depth scale.                                                        |
| `view.set-branch-scale-mode`          | `{ mode: 'auto' | 'manual' }`                                                                             | Allocate topology width automatically or use `branchScale`.                    |
| `view.set-branch-width-scale`         | `{ scale }`                                                                                                | Set branch width scale.                                                        |
| `view.set-leaf-spacing`               | `{ spacing }`                                                                                              | Set leaf row spacing.                                                          |
| `view.set-auto-collapse-threshold`    | `{ threshold }`                                                                                            | Set the automatic collapse threshold.                                          |
| `view.set-metadata-scale`             | `{ scale }`                                                                                                | Set metadata track width scale.                                                |
| `view.set-metadata-gap`               | `{ gap }`                                                                                                  | Set gap between metadata tracks.                                               |
| `view.set-metadata-row-scale`         | `{ scale }`                                                                                                | Set metadata row height scale.                                                 |
| `view.set-label-font-size`            | `{ size }`                                                                                                 | Set label font size.                                                           |
| `view.set-label-font-family`          | `{ family }`                                                                                               | Set label font family.                                                         |
| `view.set-clade-annotation-font-size` | `{ size }`                                                                                                 | Set font size for all clade annotation labels.                                 |
| `view.set-tip-alignment`              | `{ alignment: 'tip' | 'label' }`                                                                          | Align rectangular labels or enable circular tip-to-track guides.               |
| `view.set-branch-colour-attribute`    | `{ attribute: string | null }`                                                                            | Color branches by a numeric metadata column or disable the mapping.            |
| `view.set-internal-node-marker`       | `{ attribute?, encoding?, color?, categories? }`                                                           | Map support or internal-node attributes to split markers.                        |
| `view.set-tree-style-attributes`      | `{ nodeDiameterAttribute?, nodeColorAttribute?, branchWidthAttribute?, branchColorAttribute? }`            | Map exact node-circle and branch style values to data attributes.              |
| `view.set-pretty-terminal-branches`   | `{ enabled }`                                                                                              | Decorate branches entering terminal leaves.                                    |
| `view.set-conditional-style-rules`    | `{ rules }`                                                                                                | Replace ordered metadata-driven style rules.                                   |
| `view.set-collapsed-wedge-options`    | `{ shape?, fill?, fillAttribute?, fillOpacity?, gap?, minBody?, allowOverlap?, sizeAttribute?, sizeScale?, sizeTarget?, lengthMode?, sizeRange?, outline?, labelDeclutter?, labelOrientation? }` | Shape, fill, spacing, labels and data sizing for collapsed clade wedges, plus the clade-background outline. See [Collapsed wedge options](#collapsed-wedge-options). |
| `view.set-node-circles-visible`       | `{ visible }`                                                                                              | Show or hide all data-defined node circles.                                    |
| `view.toggle-labels`                  | `{}`                                                                                                       | Toggle leaf labels.                                                            |
| `view.toggle-support-labels`          | `{}`                                                                                                       | Toggle support labels.                                                         |
| `view.set-show-support`               | `{ visible }`                                                                                              | Set support-label visibility.                                                  |
| `view.set-highlighted-path`           | `{ path }`                                                                                                 | Highlight a path by stable keys.                                               |
| `view.clear-highlighted-path`         | `{}`                                                                                                       | Clear the highlighted path.                                                    |
| `view.toggle-label-overlap`           | `{}`                                                                                                       | Toggle `allowLabelOverlap` (Controls: **Auto-cull overlaps**).                 |
| `view.toggle-metadata`                | `{}`                                                                                                       | Toggle metadata track visibility.                                              |
| `view.set-metadata-visibility`        | `{ visible }`                                                                                              | Set metadata track visibility.                                                 |
| `view.toggle-figure-legend`           | `{}`                                                                                                       | Toggle figure legends without explicit section settings.                                   |
| `view.set-figure-legend-visibility`   | `{ visible }`                                                                                              | Set visibility for legends without explicit section settings.                                       |
| `view.set-figure-legend-section`      | `{ sectionIndex }`                                                                                         | Display one legend section in the figure; use `null` for all sections.         |
| `view.set-figure-legend-placement`    | `{ sectionKey, visible?, x?, y? }`                                                                         | Set per-section figure legend visibility and position.                         |
| `view.set-figure-legend-title`        | `{ sectionKey, title }`                                                                                    | Rename a displayed figure legend title.                                        |
| `view.set-figure-legend-item-label`   | `{ sectionKey, itemKey, label }`                                                                           | Rename a displayed figure legend item label.                                   |
| `view.reset-controls`                 | `{}`                                                                                                       | Reset density control values.                                                  |
| `view.reset-panel-geometry`           | `{}`                                                                                                       | Reset persisted stage panel geometry.                                          |
| `view.save`                           | `{ name, setAsDefault? }`                                                                                  | Save the current view as a named session view.                                 |
| `view.rename`                         | `{ id, name }`                                                                                             | Rename a saved view.                                                           |
| `view.delete`                         | `{ id }`                                                                                                   | Delete a saved view.                                                           |
| `view.set-default`                    | `{ id: string | null }`                                                                                   | Set or clear the default saved view.                                           |
| `view.apply`                          | `{ id }`                                                                                                   | Apply a saved view.                                                            |

`view.zoom` multiplies the current zoom by `factor`. `panX` and `panY` are
independent: each sets that axis when given, and an omitted axis keeps its
current value. `view.rename`, `view.delete`, `view.set-default` and `view.apply`
fail with `command.target-not-found` for an id that is not in `getSession().views`.

### Collapsed wedge options

`fillAttribute` names the node attribute holding the color that the `attribute`
fill reads; `null` clears it. `fillOpacity` (0 to 1) sets the translucency of the
`branch` and `attribute` fills.

`labelDeclutter` pushes crowded wedge labels outward on leader lines instead of
seating them at the wedge tip. `labelOrientation` reads them along the incoming
branch (`branch`) or outward from the center (`bearing`).

`lengthMode` sets the length of a width-sized radial wedge: `footprint`
(default) or `max-path`, the longest summed root-to-tip path in the clade.
`max-path` applies only when branch lengths are shown; otherwise wedges keep
the footprint length.

### Collapsed-clade spacing

`collapsedCladeSpacing` accepts `proportional` or `compact` and defaults to
`proportional`. Proportional spacing gives each collapsed clade one layout slot
per descendant leaf. Compact spacing gives it at most 12 slots. Open leaves
use one slot in both modes. Rectangular rows, circular branches, collapsed
wedges, and metadata cells use the same allocation.

In compact rectangular layouts, TreeViz limits a wedge triangle to three times
its body height. A dashed guide runs to the full-depth label and metadata
attachment. Triangle width is a display size. It does not encode branch length
or descendant count.

Compact circular spacing uses automatic node angles. TreeViz keeps the stored
`circularAngleAttribute` in the session and named views, but does not apply it
until `collapsedCladeSpacing` returns to `proportional`. The node-angle picker
is disabled while compact spacing is active.

Circular collapsed wedges honor `collapsedWedgeShape: 'triangle'`. Circular
triangles retain sectors when the span is too wide or shallow for a
forward-pointing triangle.

### Circular opening and fills

These `view.set-layout` arguments are saved in the session and named views.
They affect circular layout only.

| Argument | Values | Default |
| --- | --- | --- |
| `circularOpeningAngle` | Opening width in degrees, 0–350 | `0` (full circle) |
| `circularOpeningAutoFit` | Fit the opening to horizontal track names, keeping their edge fixed | `false` |
| `circularRotation` | Clockwise rotation in degrees, -180–180; zero centers the opening at the top | `0` |
| `circularAngleAttribute` | Node attribute containing angles in degrees, or `null` for automatic angles | automatic |
| `circularOpeningColor` | `#RRGGBB` or `null` for transparent | `null` |
| `circularInteriorColor` | `#RRGGBB` or `null` for transparent | `null` |

The interior fill sits behind branches and clade backgrounds and ends at the
inner edge of the metadata rings. The opening fill extends to the outer ring.
Without rings, both end at the tree's outer radius. A full circle omits the
opening fill. Fill colors stay unchanged across themes and appear in Canvas,
SVG, and PNG output.

```js
await window.__treeviz.execute('view.set-layout', {
  layout: 'circular',
  circularOpeningAngle: 90,
  circularOpeningAutoFit: true,
  circularRotation: 45,
  circularOpeningColor: '#ffffff',
  circularInteriorColor: '#ffffff'
})
await window.__treeviz.execute('view.set-tip-alignment', { alignment: 'label' })
```

Auto-fit closes the opposite edge to the measured track names while keeping
the label edge fixed. It updates when names, visible tracks, ring widths, or
the viewport change. Zoom and pan do not change the fit. With no readable
names, auto-fit retains the manual opening.

In circular layout, `alignment: 'label'` draws guides from terminal tips to
the inner metadata edge, even when leaf labels are hidden. The guides require
visible metadata. Use `'tip'` to turn them off. The same setting aligns labels
in rectangular layout and is ignored in radial layout.

Set `showScaleBar: false` through `view.set-layout` to hide the distance scale
without changing branch lengths or node positions. The default is `true`. The
checkbox is **Controls > Layout > Scale bar**. The setting persists in sessions
and named views.

### Imported circular angles

`circularAngleAttribute` selects a node attribute containing
angles from 0 through 360 degrees. Finite numbers and nonempty numeric strings
are accepted. Each missing, Boolean, nonfinite, or out-of-range value uses that
node's automatic angle. Bound leaf-table columns are not used for angles.

The value maps proportionally into the circular sweep, starting at the edge
set by the opening and rotation. For a full circle with zero degrees pointing
right and increasing clockwise, use:

```js
await window.__treeviz.execute('view.set-layout', {
  layout: 'circular',
  circularOpeningAngle: 0,
  circularRotation: 90,
  circularAngleAttribute: 'paper_angle_degrees'
})
```

The setting affects nodes, connectors, and collapsed spans. Keep angle values
in tree traversal order when using arc connectors or collapsed clades. Select
the key with **Controls > Layout > Node angles (degrees)**, or pass
`circularAngleAttribute: null` to restore automatic angles. The setting persists
in sessions and named views. Rectangular and radial layouts ignore it.
Reordering children leaves imported angles attached to their nodes; clear the
setting to lay out the new order.

### Imported radial positions

`radialXAttribute` and `radialYAttribute` select node attributes for a
radial layout. Supply both keys. Every node must have both coordinates as
finite numbers or nonempty numeric strings. TreeViz draws straight edges
between those positions and derives collapsed clade outlines from the same
coordinates. Positive Y points down the screen.

```js
await window.__treeviz.execute('view.set-layout', {
  layout: 'radial',
  radialXAttribute: 'paper_x',
  radialYAttribute: 'paper_y',
  showScaleBar: false
})
```

If exactly one key is set, or any node has a missing, Boolean, blank,
nonnumeric, or nonfinite coordinate, TreeViz uses automatic radial layout and
reports `render.radial-coordinates-invalid`. Bound metadata-table columns do
not supply positions. Branch lengths and branch spacing do not move imported
positions. The camera still supports zoom, pan, and fit.

Pass both attributes as `null`, or choose **Automatic** in both **Node X
coordinate** and **Node Y coordinate** selectors under **Controls > Layout**,
to restore automatic radial layout. The selections persist in sessions, named
views, and undo history. Rectangular and circular layouts ignore them.

## Tree commands

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
| `tree.ladderize`                            | `{ direction: 'asc' | 'desc' }` | Ladderize the tree.                                         |
| `tree.sort-by-branch-length`                | `{ direction: 'asc' | 'desc' }` | Sort clades by branch length.                               |
| `tree.collapse-by-support`                  | `{ threshold }`                  | Collapse clades below a support threshold.                  |

Every command above that takes a `stableKey` (or `leafKeys`) fails with
`command.target-not-found` when the key is not a node of the current tree, and
writes nothing. `tree.rename-leaf` and `tree.reroot-at-outgroup` also fail with
`command.invalid-target` when given an internal node. `tree.extract-subtree`
returns `{ session, keyMap }`; `keyMap` is a plain object (it survives JSON and
`page.evaluate`) that maps every stable key not in the subtree to `null`.

## Clade annotations and support

`tree.style-clade` accepts a narrow `patch` object for visual styling:

- Branch styling: `color`, `lineWidth`, `dashPattern`.
- Tip label styling: `labelColor`, `labelBold`, `labelItalic`,
  `labelFontSize`.
- Clade annotations: `label`, `cladeLabelColor`, `cladeLabelBold`,
  `cladeLabelFontSize`, `cladeLabelPlacement`, `cladeLabelOffsetX`,
  `cladeLabelOffsetY`.
- Clade underlay: `cladeBackground`. `cladeLabelBackground` is still accepted
  as a legacy alias.
- Fitted radial underlay padding: `cladeBackgroundPadding` sets nonnegative
  pixel padding before zoom for this clade only. Omitting the field keeps
  automatic padding; `undefined` in a style patch restores it.
- Collapsed wedge fill: `wedgeFill`, read from the clade's own entry only.
- Two-color fills: `cladeBackgroundGradient` and `wedgeFillGradient`, each
  `{ startColor, endColor }`. Colors interpolate from the clade root toward its
  descendants. Endpoints accept `#rrggbb` and `rgba(r,g,b,a)`. These fields
  apply only to the selected clade.
- Node/leaf markers: `internalDotSize`, `leafShape`,
  `nodeCircleDiameter`, `nodeCircleColor`.

Branch styling applies to the target clade root and its descendants while the
clade remains expanded; collapsing is not required to color the clade. A
hand-set `color` wins over `branchColorAttribute` and rule colors on the clade
and its descendants, wedge outline included; Reset clade style brings the data
color back.

A `patch.label` on an expanded internal node renders a clade-annotation label in
rectangular, circular, and radial layouts. If the same clade is collapsed,
TreeViz uses that label text for the collapsed wedge label.

Clade-annotation labels reserve readable white backing before metadata tracks:
a measured column in rectangular layout and a measured radial lane in
circular/radial layouts. The reserved space follows the label text and
`cladeLabelFontSize`, so tracks start after the label box as clade labels grow
or shrink.

`cladeBackground` draws a translucent region from the clade root to the
descendant tips: a band in rectangular layout, a sector in circular layout, and
a hull around the clade's tips in radial layout, which has no center to sweep a
sector about. The drawn region is a click target: left-click selects the clade
and tints the region, and right-click opens the clade menu, where Style > Clade
underlay recolors it.

`cladeBackgroundGradient` draws a background without a separate solid
`cladeBackground`. A gradient takes precedence over the corresponding solid
fill. `wedgeFillGradient` also replaces the global wedge fill mode and its
opacity. Use `rgba(r,g,b,a)` endpoints for translucent gradients. If the root
and descendant extents coincide, both renderers use a solid `endColor` fill.
Pass an explicit `undefined` for a gradient field through the JavaScript API
to remove it while preserving the other clade styles. Canvas and SVG exports
use the same gradient direction and extent.

Set `cladeLabelPlacement: 'node'` to center horizontal text on an internal or
terminal node. It uses the annotation text, color, weight, size, and offsets,
without a white backing or reserved label lane. A terminal node gets one
annotation instead of a second tip label. Hidden descendants and collapsed
clades retain their normal visibility rules. The default placement is
`'clade'`.

In radial layout, a clade with a background also accepts `background-top`,
`background-top-left`, `background-top-right`, `background-left` and
`background-right`. These seat the label, unrotated, on the drawn background,
and the seated label replaces a collapsed clade's wedge label. Other layouts
treat these values as `'clade'`.

`cladeLabelFontSize` accepts fractional sizes from 1 to 96 pixels. Set the
placement in **Style clade > Clade annotation**.

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

## Continuous attribute legends

`session.legends` accepts custom swatches and continuous size/color scales.
`orientation` accepts `vertical` (the default) or `horizontal`. A vertical
ramp runs from the smaller value at the top to the larger value at the bottom;
a horizontal ramp runs from left to right. `sizeRange` gives the ramp thickness
at those endpoints, and `colors` supplies evenly spaced color stops. Tick
positions use the selected `linear` or `sqrt` transform.

For a loaded session whose node and branch attributes encode sequence counts:

```js
const api = window.__treeviz
const session = api.getSession()
await api.execute('session.restore', {
  snapshot: {
    ...session,
    legends: [{
      kind: 'continuous-scale',
      title: 'Node',
      axisLabel: 'Sequence count',
      colors: ['#BEBEBE', '#018571', '#80cdc1', '#dfc27d', '#a6611a'],
      domain: [1, 3000000],
      sizeRange: [0.48, 32],
      transform: 'sqrt',
      ticks: [1, 83800, 334000, 751000, 1330000, 2080000, 3000000],
      scale: 1.6
    }],
    view: {
      ...session.view,
      figureLegendVisible: true,
      figureLegendSectionIndex: null
    }
  },
  skipAutoApplyDefault: true
})
```

The domain must increase, ticks must fall within it, and a square-root domain
must be nonnegative. `sizeRange` must be nondecreasing and its maximum must be
positive. Equal positive endpoints draw a constant-thickness rectangular ramp.

`scale` is optional, defaults to `1`, and accepts finite values from `0.1` to
`4`. It scales the ramp, spacing, stroke, axis, ticks, and text. A standalone
continuous figure legend has no frame or fill. Its regular-weight title is
centered above the ramp. The side Legend panel keeps its normal container.

Add `secondaryAxis: { axisLabel, domain, transform, ticks }` for a separate
scale on the right. Each axis positions ticks using its own domain and
transform. For percentage colors with count-scaled sizes, use a primary
`domain: [0, 100]` and `transform: 'linear'`, with a count domain and
`transform: 'sqrt'` in `secondaryAxis`:

```js
{
  kind: 'continuous-scale',
  title: 'Edges',
  axisLabel: 'Percent of OTUs identified',
  colors: ['#a000a0', '#ff6f3c', '#ffd21f', '#c8c8c8'],
  domain: [0, 100],
  sizeRange: [0.48, 32],
  transform: 'linear',
  ticks: [0, 50, 100],
  orientation: 'horizontal',
  secondaryAxis: {
    axisLabel: 'Number of reads',
    domain: [302, 250000000],
    transform: 'sqrt',
    ticks: [302, 62600000, 250000000]
  }
}
```

Axis transforms affect tick positions. Color stops and ramp thickness vary
linearly along the ramp. On a horizontal legend, the primary ticks and label
are upright below the ramp; the secondary ticks and label are upright above
it. On a vertical legend, the primary axis is on the left and the secondary
axis is on the right. Both axis domains must increase, square-root domains
must be nonnegative, and each tick must be within its own domain.

The legend describes an encoding; it does not calculate node or branch
attributes. Use the same transform and domain when computing those display
values. Continuous legends are available in session JSON. TOML `[[legend]]`
tables define swatch legends only.

Use `view.set-figure-legend-placement` with
`{ sectionKey: 'custom:0', visible: false }` to hide the first custom legend
in the figure and export. Set `visible: true` to show it; provide both `x`
and `y` to move it. Custom legend keys use zero-based indices. Explicit
section visibility overrides `view.set-figure-legend-visibility`,
which controls sections without their own placements.

## Data-defined node and branch styling

Use `view.set-tree-style-attributes` when the tree or metadata table already
contains exact visual values. Diameter and width values are interpreted as
pixels. Color values are used as CSS color strings.

Internal nodes read their node attributes, such as values from Newick/Nexus
comments. Terminal nodes read their node attributes first and then fall back to
the bound metadata row. Branch style attributes are
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

`view.set-branch-colour-attribute` maps a numeric metadata column to a branch
color gradient. Exact branch color values from
`view.set-tree-style-attributes` take precedence when both mappings are active.

Use `view.set-pretty-terminal-branches` to thicken and cap only the branch
stubs entering terminal leaves. It works in rectangular, circular, and radial
layouts and preserves each branch's current color and mapped width.

```js
await api.execute('view.set-pretty-terminal-branches', { enabled: true })
```

Use `view.set-conditional-style-rules` for threshold, category, missing-value,
boolean, text, regex, quantile, or rank styling. Source values resolve like
exact styling attributes: `support`, `meta:<key>`, node attributes, then
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

## Track commands

| Command         | Args                                  | Effect                 |
| --------------- | ------------------------------------- | ---------------------- |
| `track.add`     | `{ kind, columnKey, insertAtIndex? }` | Add a metadata track.  |
| `track.remove`  | `{ trackId }`                         | Remove a track.        |
| `track.update`  | `{ trackId, patch }`                  | Update a track config. |
| `track.reorder` | `{ order }`                           | Reorder tracks by id.  |

`track.add` and `track.update` accept only `columnKey` values that exist in
`getSession().metadata.columns`, so import metadata first. `track.update`
applies the whole patch or none of it: an unknown key (`palete`), `id`, `kind`,
a key that belongs to another track kind, or an invalid value fails with
`command.invalid-patch`. `track.reorder` needs every current track id exactly
once, and `track.remove` needs an existing id. Most rejected `track.update` and
`track.reorder` calls also push the matching `track.not-found`,
`track.invalid-patch` or `track.invalid-order` diagnostic. A patch that names a
missing metadata column fails with `command.target-not-found` and pushes no
diagnostic.

Supported track kinds are `color-strip`, `gradient`, `heatmap`, `bar`,
`stacked-bar`, `text`, and `binary-dots`. Use `stacked-bar` for composition per
tip: it takes `columnKeys` and splits one bar per leaf into a segment per
column, with `normalize: true` rescaling each row to fill the track.

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


### Connections

Connections join leaves or named internal nodes. Store them on the session as
`connections: [{ id, title, visible, geometry?, pairs }]`. `geometry` is
`'ribbon'` by default; `'straight'` draws constant-width line segments. Each
pair is `{ from, to, label?, color?, width?, opacity? }`.

```js
const session = api.getSession()
await api.execute('session.restore', {
  snapshot: {
    ...session,
    connections: [{
      id: 'acquisitions',
      title: 'Gene acquisitions',
      visible: true,
      geometry: 'straight',
      pairs: [{
        from: 'Archaeal_clade',
        to: 'Bacterial_leaf',
        label: 'illustrative transfer',
        color: '#b24a3a',
        width: 1.5,
        opacity: 0.6
      }]
    }]
  }
})
```

Ribbon links are bowed, filled, tapered paths. Straight links are native line
operations. Both use the pair's color, width, and opacity. Connection TSV files
may include `label`, `color`, `width`, and `opacity` columns. The figure legend
groups pairs by color and uses the first non-empty label for each color.

For `#rgb` and `#rrggbb` colors, opacity below 1 is encoded as `rgba(...)`; the
default opacity is 0.45. Other color syntaxes pass through unchanged. The layer
is named `connections`, so an export carries `data-tv-layer="connections"`.

Endpoint matching is exact and case-sensitive. A leaf-name match takes
precedence over an internal node with the same name. Otherwise, exactly one
internal node must have that name. Use unique internal names when connections
target clades.

TreeViz omits a pair and reports `connections.ambiguous-endpoint` when several
internal nodes match, `connections.unbound-endpoint` when no node matches,
`connections.hidden-endpoint` when an endpoint is hidden or lies below a hidden
clade, and `connections.collapsed-endpoint` when a collapsed clade leaves no
rendered position for the endpoint. `connections.self-link` and
`connections.coincident-endpoints` also omit their pairs.

### Node marks

Node marks are drawn at internal nodes rather than in the metadata band. They
read from `session.import-node-metadata`, not from the leaf binding.

| Command            | Args                                              | Effect                          |
| ------------------ | ------------------------------------------------- | ------------------------------- |
| `nodemark.add`     | `{ kind: 'pie', columnKeys, style?, palette?, sizeBy?, maxRadius? }` | Add a node mark; `style` is `pie` (default), `donut`, or `bar`. |
| `nodemark.remove`  | `{ index }`                                       | Remove a node mark.             |
| `nodemark.update`  | `{ index, patch }`                                | Update a node mark.             |

Slice angles come from each column's share of its row total. A node whose
columns are all zero or missing draws nothing rather than an empty circle. When
an edit destroys a clade, its mark is dropped with a diagnostic rather than
reattached to a different clade.

## Selection and search commands

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
| `view.hover`             | `{ key: string | null }` | Set or clear hover state.            |
| `view.search`            | `{ query }`               | Match leaf names, leaf labels and collapsed-clade labels; a hit inside a collapsed clade resolves to the wedge. Hits are stable keys in `view.searchHits`. |

`selection.set`, `selection.add`, `selection.toggle`, `selection.select-clade`
and `view.hover` (with a key; `null` always works) fail with
`command.target-not-found` for a key that is not a node of the tree, and change
nothing. Any node counts, internal or leaf, including one inside a collapsed
clade. For a list (`keys`) the whole command fails if any key is unknown: `message`
names the first one with close alternatives and says how many others are
unknown. When more than one key is unknown, `details.unknownKeys` lists up to
20 of them. `selection.remove`
does not check its keys, so it can clear a key whose node was pruned.

These commands run in call order like any other, so a `view.hover` or
`selection.set` queued behind a prune can name a node that is gone by the time
it runs. Treat `command.target-not-found` there as "the tree changed" and read
the selection again.

## History commands

| Command         | Args | Effect                           |
| --------------- | ---- | -------------------------------- |
| `history.undo`  | `{}` | Undo the previous document edit. |
| `history.redo`  | `{}` | Redo the next document edit.     |
| `history.clear` | `{}` | Clear the undo/redo ring.        |

## Export commands

| Command               | Args                                     | Effect                                               |
| --------------------- | ---------------------------------------- | ---------------------------------------------------- |
| `export.newick`       | `{}`                                     | Return Newick text.                                  |
| `export.nexus`        | `{ taxaBlock? }`                         | Return Nexus text.                                   |
| `export.leaf-names`   | `{ stableKey, format, includeMetadata }` | Return leaf names under a clade as TXT, CSV, or TSV. |
| `export.metadata-tsv` | `{}`                                     | Return the current metadata table as TSV.            |

Use `session.save` to download a full `.treeviz.json` session. Newick, Nexus,
and metadata exports do not preserve the full visualization state. Each data
export returns `{ content, filename, mimeType }` in `ExecuteResult.value`.

## Metadata import pattern

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

`applyTrackRecommendations` returns one `{ recommendation, result }` per
recommendation, in order. It holds the command queue while it runs, so no other
command can run between a recommendation's `track.add` and its `track.update`;
commands issued meanwhile run afterwards. A recommendation that fails (an
unknown column, or a track that already exists, code
`track.duplicate-recommendation`) reports its own result and the rest are still
applied.

See [`docs/METADATA.md`](METADATA.md) for the metadata table format.

## Layout QA pattern

```js
const api = window.__treeviz

await api.execute('view.set-layout', { layout: 'rectangular' })
await api.execute('view.set-metadata-gap', { gap: 0 })
await api.execute('view.set-branch-scale', { scale: 0.7 })

const { metrics, renderDiagnostics } = await api.whenSettled()
const diagnostics = api.getDiagnostics()
const { dataUrl } = await api.exportImage()
```

Call `whenSettled()` after each logical batch of changes, then read metrics and
diagnostics. `getLayoutMetrics()` counts `labelsVisible`, `labelsCulled`,
`labelCollisions` and `labelsClipped` at the current camera. Labels hold their
screen size above zoom 1, so to judge legibility at a target zoom call
`view.zoom`, await `whenSettled()`, and read the metrics again. Look at the
exported image before calling visual changes complete.

Radial figures with collapsed wedges add `wedgeOverlapPairs`, pairs of wedge
fills that intersect, and `wedgeBranchCrossings`, branches of other lineages
that run through a wedge, both measured on the drawn polygons. Either above
zero puts `metrics.wedge.overlap` in `warnings`. Both fields are absent when
the figure draws no such wedge.

`getRenderDiagnostics()` returns `{ code, message }` items that the last frame
could not draw. Read it after the render when the requested figure includes
connections, node marks, or other data-dependent layers.

## Wait for the render

`whenSettled(opts?)` resolves with `{ revision, metrics, renderDiagnostics }`
once the figure on screen matches the latest state:

1. fonts are ready;
2. a frame has rendered since the latest document, view or camera change, so
   `metrics` belong to that change and not to the previous figure;
3. nothing has changed, and no frame has rendered, for two animation frames and
   about 250 ms. The 250 ms outlasts the 150 ms rebuild that follows a camera
   change (label culling, hit boxes). A busy main thread restarts the wait.

`metrics` is `getLayoutMetrics()` and `renderDiagnostics` is
`getRenderDiagnostics()` at that frame. `revision` counts the document, view and
camera changes seen so far; equal revisions mean the same state. It watches the
store, not command events, so `view.*` commands and UI gestures count too.

It rejects with an `Error` after `opts.timeoutMs` (default 30000) that names what
it was still waiting for: no frame yet (no session loaded, or the canvas is not
mounted), a hidden page, no frame after the latest change, fonts loading, or
metrics still changing. After an edit it took 0.3 to 2 s on Examples 1 and 6 in
headless Chromium. Straight after a session load the app first runs its own
set-up commands (Example 1 repositions its 23 legend sections one command and
one redraw at a time), which took 15 to 20 s there, and 5 to 7 s for a large
session on a loaded machine. The 30 s default covers that; pass a larger
`timeoutMs` on a slow machine or for a very large tree.

```js
await api.execute('view.zoom', { factor: 2 })
const { metrics } = await api.whenSettled()
console.log(metrics.labelsVisible, metrics.labelsCulled) // at 2x, not at fit
```

## Export an image

`exportImage(opts?)` resolves with `{ dataUrl, width, height }`. It rasterizes
the SVG that `exportSvg()` returns through the same crop and canvas path as the
Export panel, so an agent gets a PNG without an external renderer. It rejects when no render
backend is mounted. Call `whenSettled()` first.

| Option       | Default                                         | Effect                                                                         |
| ------------ | ----------------------------------------------- | ------------------------------------------------------------------------------ |
| `format`     | `'png'`                                         | `'png'` or `'svg'`.                                                            |
| `scale`      | `1`                                             | Multiplies the natural CSS-pixel size. PNG is clamped to 16384 px a side.      |
| `background` | theme canvas color (PNG), transparent (SVG)    | A CSS color, or `null` for a transparent image.                               |
| `crop`       | `true`                                          | Crop to the painted content plus 16 px, as the panel does. `false`: full canvas. |

`width` and `height` are the PNG pixel size, or the SVG size in CSS pixels times
`scale`. The SVG data URL is percent-encoded (`decodeURIComponent` after the
comma) and can be several megabytes for a large tree.

```js
await api.whenSettled()
const { dataUrl, width, height } = await api.exportImage({ scale: 2, background: '#ffffff' })
// In Playwright: fs.writeFileSync('figure.png', Buffer.from(dataUrl.split(',')[1], 'base64'))
```

## Find nodes

`findNodes(query)` returns `{ stableKey, name, kind, depth, leafCount, parentKey }`
for leaf and internal nodes, in tree order. `view.search` only matches leaves and
collapsed clades by substring; this matches every node and adds regex and
metadata tests. A `label` field appears when `tree.style-clade` gave the node a
clade label that differs from its name.

| Field    | Meaning                                                                                                         |
| -------- | --------------------------------------------------------------------------------------------------------------- |
| `text`   | Case-insensitive substring of the node name or clade label.                                                     |
| `regex`  | Pattern tested against the node name and clade label. `flags` sets its flags, for example `'i'`.                |
| `meta`   | `{ key, op, value? }` with `op` one of `eq`, `ne`, `lt`, `lte`, `gt`, `gte`, `contains`, `exists`.              |
| `kind`   | `'leaf'`, `'internal'` or `'any'` (default).                                                                    |
| `limit`  | Maximum results. Default 50. A result as long as `limit` may be cut short: raise it.                            |

Every field given must match. `meta.key` reads `support`, then node
attributes (a `meta:` prefix is optional), then the bound leaf row for a leaf or
the bound node-metadata row for an internal node. Numbers compare numerically
when both sides are numeric, else as text. A missing or empty value satisfies no
comparison; use `{ op: 'exists', value: false }` to find it. An invalid regex or
argument throws an `Error` that names the problem. With no session it returns
`[]`.

```js
api.findNodes({ text: 'coli', kind: 'leaf', limit: 10 })
api.findNodes({ regex: '^bsub_\\d+$', flags: 'i' })
const [clade] = api.findNodes({ kind: 'internal', meta: { key: 'support', op: 'gte', value: 0.9 } })
await api.execute('tree.collapse-clade', { stableKey: clade.stableKey })
```

## Describe the figure

`describeFigure()` returns a compact summary of the figure, meant to be read by
a language model. It throws when no session is loaded.

| Key                        | Contents                                                                                             |
| -------------------------- | ---------------------------------------------------------------------------------------------------- |
| `name`, `layout`, `view`   | Session name, layout, and the settings that matter now. Defaults with no effect are left out.       |
| `leaves`                   | `total`, `visible` (own row or tip), `collapsed` (in a wedge), `hidden`, `collapsedClades`, `hiddenClades`. |
| `tracks`, `tracksTotal`    | `{ id, kind, column, visible, missingPct }`; `missingPct` is the share of all leaves with no value. |
| `legends`, `legendsTotal`  | `{ key, title, visible, entryCount }`; `key` is the `sectionKey` of `view.set-figure-legend-placement`. |
| `binding`                  | `null` without metadata, else `rowKeyColumn`, `matched`, `unmatchedLeaves`, `unmatchedRows`, `duplicateLeaves`, and up to 10 `unmatchedLeafNames`. |
| `labels`, `render`         | Label culling counts, and occupancy, track density and `p75BranchPx`, at the current camera. `null` before the first frame. |
| `warnings`                 | `warnings` from `getLayoutMetrics()`.                                                                |
| `diagnosticsSinceLastCall` | Diagnostics logged since the previous `describeFigure()` call (all of them, for the first).          |

Lists are capped at 12 tracks and 10 legend sections so the summary stays a few
kilobytes on figures with dozens of each. When a list is longer than its cap,
hidden and mostly-missing tracks and the legend sections the figure shows take
the slots first; entries keep their original order. Read the totals to see
what was left out, and `getSession()` for everything. It reads the live session,
so call `whenSettled()` first if `labels` and `render` must match the latest edit.

```js
await api.whenSettled()
const figure = api.describeFigure()
// { name, layout: 'circular', leaves: { total: 1204, visible: 1204, ... },
//   tracks: [{ id, kind: 'color-strip', column: 'Habitat', visible: true, missingPct: 0 }, ...],
//   binding: { matched: 1204, unmatchedLeaves: 0, unmatchedLeafNames: [] }, warnings: [...] }
```

## Diagnostics

`getDiagnostics()` returns the command, import and session diagnostic log.
`getRenderDiagnostics()` reports items the latest rendered frame could not draw.
Read both after the figure renders.

`getDiagnostics()` returns a copy, so a snapshot taken earlier does not change
later. Each entry has a `seq` that increases with every diagnostic and is never
reused. Pass `{ since }` to get only entries with a greater `seq`, which shows
what one batch of commands added. `clearDiagnostics()` empties the log; `seq`
keeps counting, so a mark taken before it stays valid. `session.import-tree` and
`session.restore` also clear the log; metadata imports add to it.

```js
const mark = api.getDiagnostics().at(-1)?.seq ?? 0
await api.execute('view.set-layout', { layout: 'radial' })
const added = api.getDiagnostics({ since: mark }) // [] when nothing was logged
api.clearDiagnostics()
```

Each diagnostic is structured:

```ts
interface SequencedDiagnostic {
  seq: number
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
