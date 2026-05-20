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
- duplicate row keys should be surfaced as warnings;
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
- Manual single-node webapp edits: Inspector controls backed by
  `tree.style-clade` patch fields `color`, `lineWidth`, `labelColor`,
  `labelFontSize`, `nodeCircleDiameter`, and `nodeCircleColor`.
- Numeric branch coloring: `view.set-branch-colour-attribute`.
- Rerooting: `tree.reroot`, `tree.reroot-at-outgroup`, `tree.midpoint-reroot`.
- Collapsing, expanding, hiding, pruning: `tree.collapse-clade`,
  `tree.expand-clade`, `tree.hide-clade`, `tree.prune-clade`.
- Layout and density: `view.set-layout`, `view.set-branch-scale`,
  `view.set-leaf-spacing`, `view.set-metadata-gap`,
  `view.set-metadata-row-scale`, `view.toggle-label-overlap`,
  `view.set-scale-bar-position`.

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
