---
name: treeviz-agent
description: Use for agent-driven phylogenetic tree visualization in TreeViz: load Newick/Nexus/.treeviz.json sessions, import leaf or node metadata, choose row keys, plan tracks, style clades, add node marks, tip connections, legends and attribute names, tune layouts and label culling, check legibility at a zoom, search and inspect nodes, and export figures through the hosted TreeViz browser API.
---

# TreeViz Agent

TreeViz is a browser-based tree visualization tool. Keep biological reasoning,
file preparation, and interpretation in the agent; use TreeViz for deterministic
parsing, metadata binding, layout, styling, diagnostics, and export.

Default runtime:

```text
https://treeviz.newlineages.com/?api=1
```

Headless runtime for browser automation:

```text
https://treeviz.newlineages.com/?mode=headless&api=1
```

This public skill does not vendor the TreeViz browser app or frontend source.
Use the hosted app unless the user explicitly provides another TreeViz runtime.

## Core Workflow

1. Open TreeViz with `?api=1` and wait for `window.__treeviz`.
2. Import a tree or restore a `.treeviz.json` session.
3. Inspect `getSession()`, `commands()`, `palettes()`, and `getDiagnostics()`.
4. For metadata, call `planMetadataImport(source, format, prompt)` before import.
5. Import metadata with the suggested row key, flags, and leaf identifier source.
6. Add or update tracks through `track.add`, `track.update`, and `track.reorder`.
7. Apply clade styles, conditional rules, node marks, or session connections as needed.
8. Tune layout with `view.set-layout`, automatic scale, spacing, labels, and legend commands.
9. Re-check diagnostics and layout metrics after each logical batch.
10. Export evidence: `.treeviz.json` for state, SVG/PNG/PDF for figures, and screenshots when visual quality is the claim.

## Visualization Defaults

- Start metadata-heavy figures in rectangular layout.
- Try circular or radial layout only when labels and metadata remain readable.
- Shape radial collapsed-clade wedges with `view.set-collapsed-wedge-options`:
  fill source, opacity, gap, minimum body, outline, and data sizing.
- Keep metadata tracks contiguous; use `metadataGap: 0` unless separation is useful.
- Keep `branchScaleMode` on `auto` unless fixed geometry is required. Setting a
  manual branch scale freezes the automatic width and spacing calculation.
- Reduce whitespace by tuning leaf spacing, metadata scale, metadata gap, label
  size, and export cropping before enlarging the canvas.
- Use palette ids from `palettes()`. Prefer `okabe-ito` for categorical data;
  `Viridis`, `Magma`, `Cividis`, or `Blues` for sequential data; and
  `blue-orange`, `RdBu`, or `BrBG` for diverging data.
- Use `categoryColors` when exact category colors must survive a session upload.
- Use `binary-dots` tracks for leaf symbols such as presence/absence markers.
- Use `displayMode: 'symbol'` or `'wedge'` for compact color-strip or bar
  lanes. Bar tracks can use ordered `bins` or `autoBins`.
- Use support labels and internal-node markers for branch support when the tree carries numeric internal-node labels.
- Use exact style attributes for data-defined node circles and branch
  width/color; enable pretty terminal branches when the user asks for styled
  leaf-facing terminal branches.
- For one-off webapp edits, use Controls > Exact styling for data attributes,
  Style clade for clade branch/label styling, and Inspector for direct
  selected-node circle diameter/color and branch width/color.
- Use `view.set-conditional-style-rules` for metadata-driven thresholds,
  ranks, missing values, and category conditions.
- Use `session.import-node-metadata` and `nodemark.add` for pie, donut, or bar
  marks at named internal nodes.
- Put tip-to-tip connections in the saved session and resolve endpoint
  diagnostics before export.
- Use explicit legend titles and item labels when exporting publication figures.
- Give attribute encodings (branch colour, node-circle colour, wedge fill) a
  legend through `legends` on the session document and readable picker names
  through `attributeLabels`; set `view.figureLegendVisible` when the figure
  should open with the legend shown.
- On crowded radial figures set `collapsedWedgeLabelDeclutter: true` and
  `allowLabelOverlap: false`; culled labels return as the reader zooms in.
- Treat high unmatched-leaf or unmatched-row counts as a binding problem to fix or report.

## Reference Loading

Load only the reference needed for the task:

- `references/browser-api.md`: command discovery, hosted API methods, current
  feature commands, and JavaScript examples.
- `references/session-workflows.md`: metadata import, session review, clade resolution, and command mapping.
- `references/render-qa.md`: automatic layout, occupancy metrics, screenshots,
  and export QA.
- `references/example-inputs.md`: deterministic 30-leaf and 100-leaf example recipes with metadata and support markers.
- `references/large-taxonomy-trees.md`: large taxonomy-tree workflows, metadata-derived categories, rerooting, and dense exports.
- `references/hosted-runtime.md`: hosted URLs, public machine-readable files, the six hosted real-data sessions, and live API smoke testing.
- `references/wrapper-api.md`: published Python 0.6.0 package and notebook workflows.

## Helper Scripts

- `scripts/check-live-api-smoke.ts`: Playwright smoke test for the hosted browser API.
- `scripts/postprocess-treeviz-export.py`: repeated SVG/PNG cleanup with Pillow
  and `rsvg-convert`.
- `scripts/reroot-newick-by-metadata.py`: repeatable Newick rerooting from TSV/CSV metadata.

## QA Rules

- Always `await` API calls before issuing dependent commands.
- Check `getDiagnostics()` after import and after major edits.
- Check `getLayoutMetrics()` after layout changes.
- Judge legibility at the zoom the reader will use: labels hold their screen
  size above zoom 1, so `labelsVisible` and `labelsCulled` at fit differ from
  the counts at 2x. Call `view.zoom`, wait for the render, read the metrics again.
- Start layout QA with `contentOccupancyX`, `contentOccupancyY`,
  `labelsClipped`, `labelCollisions`, `trackDensity`, and `p75BranchPx`.
- Do not claim visual quality from configuration alone; inspect a recent screenshot, SVG, PNG, or PDF.
- For Python-generated sessions, run `validate_session(session)` and inspect `binding_diagnostics(session)`.
- Save final state as `.treeviz.json` when a user may need to reopen or revise the visualization.
