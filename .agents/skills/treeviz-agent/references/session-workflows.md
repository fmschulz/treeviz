# TreeViz Session Workflows

Use this reference for metadata import, metadata-aware session review, clade
resolution, and translating user intent into TreeViz commands.

## New Session With Metadata

1. Open TreeViz with `?api=1`.
2. Import the tree first.
3. Inspect:
   - `getSession()` for current tree, view, tracks, and metadata state;
   - `commands()` for exact command ids and argument schemas;
   - `getDiagnostics()` for parse, binding, edit, or render issues.
4. Call `planMetadataImport(source, format, prompt)` before metadata import.
5. Review:
   - `suggestedBinding` for row key, leaf identifier, and normalization;
   - `bindingSummary` for matched and unmatched leaves/rows;
   - `checks` for consistency warnings;
   - `recommendedTracks` for prompt-derived track suggestions.
6. Import metadata with `session.import-metadata`.
7. Apply planner tracks with `applyTrackRecommendations(...)` when the user
   wants TreeViz to set up the view.
8. Continue with track, clade, or layout edits through `execute(...)`.

## Existing Session

For a loaded session that already has metadata:

1. Call `analyzeSessionMetadata(prompt)`.
2. Review checks and recommended tracks.
3. Rebind with `session.rebind` if matching is wrong or incomplete.
4. Apply or adjust tracks.
5. Save the revised session as `.treeviz.json`.

## Metadata Rules

TreeViz metadata is TSV or CSV with one header row. One column must be selected
as the row key; its values are matched to tree leaf labels by default.

Remember:

- empty cells become missing values;
- duplicate row keys are warnings and use last-value-wins semantics;
- blank row keys are skipped and reported by the browser;
- CSV is safer for quoted fields, commas, or embedded newlines;
- TSV is best for simple tabular metadata.

For user-facing details, read `docs/METADATA.md`.

## Clade Resolution

When the user names a clade indirectly, avoid screen picking.

- If taxonomy metadata is available, bind it before resolving the clade.
- Prefer `resolveClade(...)` for metadata predicates and named leaf sets.
- Use stable keys from `getSession().tree` for tree-edit commands.
- Before rerooting on a named taxon, check whether the selected leaves are
  monophyletic.
- If the MRCA is the whole tree or pulls in many unrelated leaves, report that
  before applying the edit.
- Exclude ambiguous taxonomy terms explicitly when requested, such as
  `incertae_sedis`, `incertae sedis`, `uncultured`, or local placeholders.

For repeatable file-based rerooting from metadata, use
`scripts/reroot-newick-by-metadata.py`.

## Intent To Command Map

- Metadata tracks: `track.add`, `track.update`, `track.reorder`.
- Categorical clade emphasis: `tree.style-clade`.
- Clade annotation labels: `tree.style-clade` with `patch.label`,
  `cladeLabelColor`, `cladeLabelBold`, `cladeLabelFontSize`, or
  `cladeBackground`.
- Bootstrap/support labels: `view.set-show-support`.
- Internal-node support markers: `view.set-internal-node-marker`.
- Exact node/branch style values: `view.set-tree-style-attributes`.
- Pretty terminal branches: `view.set-pretty-terminal-branches`.
- Conditional metadata styles: `view.set-conditional-style-rules`.
- Compact category or interval lanes: `track.update` with `displayMode` set to
  `symbol` or `wedge`; bar tracks use `bins` or `autoBins`.
- Internal-node metadata and marks: `session.import-node-metadata`, followed by
  `nodemark.add`, `nodemark.update`, or `nodemark.remove`.
- Tip-to-tip links: add `connections` to the session before `session.restore`.
- Manual single-node webapp edits: Inspector controls backed by
  `tree.style-clade` patch fields `color`, `lineWidth`, `labelColor`,
  `labelFontSize`, `nodeCircleDiameter`, and `nodeCircleColor`.
- Numeric branch coloring: `view.set-branch-colour-attribute`.
- Readable name on one leaf: leaf names must be unique, so keep the leaf name
  and set the displayed text with `tree.style-clade` patch `label`, which
  writes `cladeStyles[leafKey].label`. In a `treeviz.toml` this is a
  `[[branch_rule]]` with `label = "<leaf name>"` and `clade_label = "<text>"`.
  A tree with repeated leaf labels fails to parse with
  `parse.duplicate-leaf-label`.
- Rerooting: `tree.reroot`, `tree.reroot-at-outgroup`, `tree.midpoint-reroot`.
- Collapsing, expanding, hiding, pruning: `tree.collapse-clade`,
  `tree.expand-clade`, `tree.hide-clade`, `tree.prune-clade`.
- Label colour for a whole subtree: `tree.style-clade` with
  `patch.labelColor` (TOML `label_color`), inherited by leaf labels and
  collapsed-clade wedge labels alike, so one rule per domain colours a tree
  of life. It is separate from `cladeLabelColor`, which colours only the
  annotation on the selected root.
- A label reading against its neighbours: in the polar layouts text on the
  far side turns around so it is never upside down, and a clade on that
  turnover ends up mirrored. `patch.labelFlip` (TOML `label_flip`) reverses
  the choice for one label.
- Moving a label: any label can be dragged in the webapp, which writes
  `patch.cladeLabelOffsetX` / `cladeLabelOffsetY` on that clade, so the nudge
  survives saving and appears in exports. Set the same fields directly for a
  reproducible figure.
- Labels colliding in a crowded radial fan: `collapsed_wedge_label_declutter`
  in TOML (view `collapsedWedgeLabelDeclutter`) pushes a label that overlaps
  one already placed further out along its own bearing and draws a leader
  line back to its wedge. Wedge length and Branch spacing do not fix this
  case: the labels share a bearing.
- Labels that still collide: `allow_label_overlap = false` in TOML (view
  `allowLabelOverlap`, flipped by `view.toggle-label-overlap`; Controls
  **Auto-cull overlaps**) drops a label that would land on one already drawn.
  The culler judges collapsed labels at their decluttered seats. Above zoom 1
  labels keep their screen size while the tree grows, so culled labels return
  as the view zooms in.
- Legends for attribute encodings (branch colour, node-circle colour, wedge
  fill): TOML `[[legend]]` tables with `title` and
  `entries = [{ label, color }]`, compiled to the top-level `legends` array
  and shown in the Legend panel, the in-figure legend and exports.
  `figure_legend = true` in `[view]` (view `figureLegendVisible`) opens the
  in-figure legend on load. No command edits `legends`; set it on the document
  and `session.restore`.
- Readable names for node-meta keys in the Controls pickers and hover
  tooltips: TOML `[attribute_labels]` (`vc = "Domain colour"`), compiled to
  the top-level `attributeLabels` map; pickers show `Domain colour (vc)`.
- Finding a taxon or clade by name: `view.search` matches leaf names, leaf
  labels and collapsed-clade labels and writes stable keys to
  `view.searchHits`; a hit inside a collapsed clade is that clade's wedge.
  Hovering or selecting a collapsed clade (`view.hover`, `selection.set`)
  outlines its wedge.
- Crowded radial figures: `view.set-leaf-spacing` (Controls: Branch spacing)
  scales the rectangular row pitch and shapes the radial angle split, where
  each child is weighted by its leaf count raised to that power. Above 1 the
  wide clades take more of the turn, which keeps the drawing compact so it
  renders larger and crowded regions gain room.
- Layout and density: `view.set-layout`, `view.set-branch-scale-mode`,
  `view.set-branch-scale`,
  `view.set-leaf-spacing`, `view.set-metadata-gap`,
  `view.set-metadata-row-scale`, `view.toggle-label-overlap`,
  `view.set-scale-bar-position`.
- Layout choice: circular gives every leaf an equal angular slot, so a clade's
  footprint tracks taxon count. Radial draws true branch lengths, so a clade
  with longer root-to-tip depths covers more area. Pick the layout by what the
  figure should encode.

## Exact Style Workflow

When the user asks for fixed node-circle diameters, fixed node colors, branch
widths, or branch colors, prefer exact style attributes over clade styling.

1. Bind metadata for terminal leaves, or inspect tree node metadata for
   internal-node annotations.
2. Set the style mappings:

   ```js
   await api.execute('view.set-tree-style-attributes', {
     nodeDiameterAttribute: 'node_diameter',
     nodeColorAttribute: 'node_color',
     branchWidthAttribute: 'branch_width',
     branchColorAttribute: 'branch_color'
   })
   ```

3. Enable pretty terminal branches when the user wants rounded, emphasized
   terminal branch stubs:

   ```js
   await api.execute('view.set-pretty-terminal-branches', { enabled: true })
   ```

4. Check `getDiagnostics()` and `getLayoutMetrics()` after switching layouts,
   because heavy terminal strokes may need lower branch-width or leaf-spacing
   settings in dense trees.

## Internal Node Marks

Import a TSV keyed to internal-node labels, then add a pie-family mark:

```js
await api.execute('session.import-node-metadata', {
  tsv: [
    'node_id\tstate_a\tstate_b\tstate_c',
    'ancestor_1\t0.6\t0.3\t0.1'
  ].join('\n'),
  rowKeyColumn: 'node_id'
})

await api.execute('nodemark.add', {
  kind: 'pie',
  style: 'donut',
  columnKeys: ['state_a', 'state_b', 'state_c'],
  palette: 'okabe-ito',
  maxRadius: 10
})
```

`session.import-node-metadata` uses a `tsv` argument, unlike leaf metadata
import, which uses `source` plus `format`. The node names must match internal
labels in the tree. One node-mark definition renders at every bound internal
node whose component columns contain a nonzero value.
