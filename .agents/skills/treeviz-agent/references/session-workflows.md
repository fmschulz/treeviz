# TreeViz Session Workflows

Use this reference for metadata import, metadata-aware session review, clade resolution, and translating user intent into TreeViz commands.

## New Session With Metadata

1. Open TreeViz with `?api=1` so `window.__treeviz` is available.
2. Import or restore the tree first.
3. Inspect the current session:
   - `getSession()` for current tree, view, tracks, and metadata state.
   - `commands()` when you need exact command ids or argument shapes.
   - `getDiagnostics()` to catch parse, binding, edit, or render issues early.
4. If the user provided metadata or taxonomy files, call `window.__treeviz.planMetadataImport(source, format, prompt)` before importing.
5. Review the returned plan:
   - `suggestedBinding` is the best row-key, leaf-identifier, and normalization combo found automatically.
   - `bindingSummary` shows exact/normalized matches plus unmatched leaves/rows.
   - `checks` are consistency warnings to surface or fix.
   - `recommendedTracks` are track suggestions derived from the prompt and column profiles.
6. If the binding is acceptable, execute `session.import-metadata` with:
   - `source`
   - `format`
   - `rowKeyColumn`
   - `flags`
   - `leafIdentifierSource`
7. If the user wants the agent to set up the view, call `applyTrackRecommendations(plan.recommendedTracks)` after import.
8. Continue with structural, track, or view edits through `execute(...)`.

## Existing Sessions

For a loaded session that already has metadata:

1. Call `window.__treeviz.analyzeSessionMetadata(prompt)`.
2. Review `checks` and `recommendedTracks`.
3. If the binding is wrong or incomplete, rebind with `session.rebind`.
4. Apply or adjust tracks.
5. Continue with structural or view edits through `execute(...)`.

## Metadata Files

TreeViz metadata is TSV or CSV with one header row. One column must be selected as the row key; its values are matched to tree leaf labels by default.

Rules to remember:

- Empty cells become missing values.
- Duplicate row keys are accepted with last-value-wins semantics and should be surfaced as warnings.
- Use CSV when values need quoting, commas, or embedded newlines.
- TSV parsing is intentionally simple: tabs and newlines separate cells and rows.

For full user-facing guidance, read `docs/METADATA.md`.

## Clade Resolution

When the user names a clade indirectly, do not rely on screen picking if you can avoid it.

- If the user provides taxonomy metadata, bind/import that first and derive the target leaves from metadata.
- Prefer `window.__treeviz.resolveClade(...)` once the tree and relevant metadata are loaded.
- If the user names leaves or an outgroup, resolve the relevant stable key from `getSession().tree`.
- Use stable keys for all tree-edit commands.
- Prefer data-driven clade resolution over pixel-driven clicking.
- Before rerooting on a named taxon, test whether the selected leaves are monophyletic. If their MRCA is the whole tree or pulls in many unrelated leaves, report that and choose the largest concentrated clade only when that matches the user's intent.
- Exclude ambiguous taxonomy terms explicitly when requested, for example rows containing `incertae_sedis`, `incertae sedis`, `uncultured`, or local placeholder values.

For repeatable file-based rerooting from TSV/CSV metadata, use `scripts/reroot-newick-by-metadata.py` instead of rewriting a one-off parser.

## Intent To Command Map

- Metadata tracks: `track.add`, `track.update`, `track.reorder`
- Categorical branch/clade emphasis on expanded or collapsed clades:
  `tree.style-clade`
- Clade annotation labels: `tree.style-clade` with `patch.label`,
  `cladeLabelColor`, `cladeLabelBold`, `cladeLabelFontSize`, or
  `cladeBackground`
- TOML clade annotation labels: `[[branch_rule]]` with `clade_label`,
  `clade_label_color`, `clade_label_bold`, `clade_label_font_size`, and
  `clade_background`
- Clade labels reserve measured white backing before metadata tracks:
  a column in rectangular layout and a radial lane in circular/radial layouts.
  Larger `cladeLabelFontSize` / `clade_label_font_size` values move tracks
  outward automatically.
- Bootstrap/support display: `view.set-show-support` for labels and
  `view.set-internal-node-marker` for split-circle markers
- Numeric branch colouring: `view.set-branch-colour-attribute`
- Rerooting: `tree.reroot`, `tree.reroot-at-outgroup`, `tree.midpoint-reroot`
- Collapsing, expanding, hiding, pruning: `tree.collapse-clade`, `tree.expand-clade`, `tree.hide-clade`, `tree.prune-clade`
- Layout and density: `view.set-layout`, `view.set-branch-scale`, `view.set-leaf-spacing`, `view.set-metadata-gap`, `view.set-metadata-row-scale`, `view.toggle-label-overlap`, `view.set-scale-bar-position`
