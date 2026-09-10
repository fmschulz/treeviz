---
name: treeviz-agent
description: "Use for agent-driven phylogenetic tree visualization in TreeViz: load Newick/Nexus/.treeviz.json sessions, import leaf or node metadata, choose row keys, plan tracks, style clades, add node marks, tip connections, legends and attribute names, tune layouts and label culling, check legibility at a zoom, search and inspect nodes, and export figures through the hosted TreeViz browser API."
---

# TreeViz Agent

TreeViz is a browser-based tree visualization tool. Keep biological reasoning,
file preparation, and interpretation in the agent; use TreeViz for deterministic
parsing, metadata binding, layout, styling, diagnostics, and export.

Default hosted runtime:

```text
https://treeviz.newlineages.com/?api=1
```

Headless runtime for browser automation:

```text
https://treeviz.newlineages.com/?mode=headless&api=1
```

This public skill does not vendor the TreeViz browser app or frontend source.
Use the hosted app unless the user explicitly provides another TreeViz runtime.
Guide: `https://fmschulz.github.io/treeviz/AGENTS/`. Runtime entry:
`https://treeviz.newlineages.com/agent`.

## Core Workflow

1. Open TreeViz with `?api=1` and wait for `window.__treeviz`.
2. Import a tree or restore a `.treeviz.json` session. Example 1:
   Mirusviricota has 18 tracks and a fitted circular opening. Example 2: SILVA
   taxonomy has imported node angles, count-scaled nodes and branches, 50
   centered labels, and a continuous count legend.
   [Example 3](https://doi.org/10.1371/journal.pcbi.1005404.g003): TARA Oceans
   Metazoa has 550 taxa, including 275 terminal taxa, 20,212 OTUs,
   250,296,231 reads, 73 labels, imported radial X/Y coordinates, and separate
   percentage/count axes. It uses real source data. Its display geometry was
   reconstructed and aligned to the paper raster because the original
   force-layout coordinates are unavailable.
   [Example 4](https://doi.org/10.1038/nature13805) uses the published 178-tip
   source topology and branch agreement. Its pairwise transfer weights are
   explicitly synthetic because the source has no recoverable transfer matrix.
3. Inspect `getSession()`, `commands()`, `palettes()`, and `getDiagnostics()`.
4. For metadata, call `planMetadataImport(source, format, prompt)` before import.
5. Import metadata with the suggested row key, flags, and leaf identifier source.
6. Add or update tracks through `track.add`, `track.update`, and `track.reorder`.
7. Apply clade styles, conditional rules, node marks, or session connections as needed.
8. Tune layout with `view.set-layout`, automatic scale, spacing, labels, and legend commands.
9. Let fonts and the rendered frame settle, then check `getDiagnostics()`, `getRenderDiagnostics()`, and layout metrics. See the waits in `references/browser-api.md`.
10. Export evidence: `.treeviz.json` for state, SVG/PNG/PDF for figures, and screenshots when visual quality is the claim.

## Visualization Defaults

- Start metadata-heavy figures in rectangular layout.
- Try circular or radial layout only when labels and metadata remain readable.
- For circular figures, set the opening angle, rotation, auto-fit, and optional
  opening or interior fills through `view.set-layout`. Use
  `view.set-tip-alignment` with `alignment: 'label'` for tip-to-track guides.
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
- For abundance trees, store display-ready diameters, widths, and colors in
  node metadata. Add horizontal names with `tree.style-clade` and
  `{ label, cladeLabelPlacement: 'node', cladeLabelFontSize }`. Node placement
  works on internal and terminal nodes, and font size accepts fractional values
  from 1 to 96 pixels. Set `showScaleBar: false` through `view.set-layout` when
  taxonomic depth should remain visible without a distance scale.
- To preserve a source circular layout, store degrees from 0 through 360 in
  direct node metadata and select the key with `circularAngleAttribute` through
  `view.set-layout`. Opening and rotation still apply. Missing or invalid
  values fall back per node. Keep angles in traversal order for arc connectors
  and collapsed spans. Pass `null` to restore automatic angles. Rectangular and
  radial layouts ignore this setting.
- For a source radial layout, select `radialXAttribute` and `radialYAttribute`
  through `view.set-layout`, or use **Node X coordinate** and **Node Y
  coordinate** under **Controls > Layout**. Every node needs both direct
  metadata values as finite numbers or nonempty numeric strings; positive Y
  points down. An incomplete pair or invalid coordinate uses automatic radial
  layout and reports `render.radial-coordinates-invalid`. Pass both keys as
  `null`, or set both selectors to **Automatic**, to clear them. Circular and
  rectangular layouts ignore them.
- For one-off webapp edits, use Controls > Exact styling for data attributes,
  Style clade for clade branch/label styling, and Inspector for direct
  selected-node circle diameter/color and branch width/color.
- Use `view.set-conditional-style-rules` for metadata-driven thresholds,
  ranks, missing values, and category conditions.
- Use `session.import-node-metadata` and `nodemark.add` for pie, donut, or bar
  marks at named internal nodes.
- Put connections in the saved session. Endpoints use exact leaf names or
  unique internal-node names, with leaf names taking precedence. Set
  `geometry: 'straight'` for constant-width lines; the default `ribbon` is
  bowed and tapered. Resolve ambiguous, unbound, hidden, and collapsed
  endpoint diagnostics before export. Preserve unique internal labels when
  preparing a topology for clade endpoints.
- Use explicit legend titles and item labels when exporting publication figures.
  Place, move or hide sections with `view.set-figure-legend-placement` and
  `{ sectionKey, visible, x, y }`. Custom legend keys are `custom:0`,
  `custom:1`, etc. Explicit section visibility overrides the
  global `view.set-figure-legend-visibility` command.
- Give attribute encodings (branch colour, node-circle colour, wedge fill) a
  legend through `legends` on the session document and readable picker names
  through `attributeLabels`; set `view.figureLegendVisible` when the figure
  should open with the legend shown.
- For a combined numeric size/color legend, use a session JSON
  `continuous-scale` legend with `title`, `axisLabel`, `colors`, `domain`,
  nondecreasing `sizeRange` with a positive maximum, `transform`, `ticks`, and
  optional `scale` and `orientation`. `orientation: 'horizontal'` runs low to
  high left-to-right. `scale` defaults to `1` and accepts `0.1` to `4`. TOML
  legends define swatches only.
- Add `secondaryAxis: { axisLabel, domain, transform, ticks }` to a continuous
  legend when color and size need separate numeric scales. Horizontal primary
  labels are upright below and secondary labels are upright above; vertical
  axes are left and right. See `references/browser-api.md`.
- On crowded radial figures set `collapsedWedgeLabelDeclutter: true` and
  `allowLabelOverlap: false`; culled labels return as the reader zooms in.
  `collapsedWedgeLabelOrientation: 'branch'` reads each label along the
  branch entering its clade.
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
- `references/hosted-runtime.md`: hosted URLs, public files, the current example,
  and live API smoke testing.
- `references/wrapper-api.md`: published Python 0.6.0 package and notebook workflows.

## Helper Scripts

- `scripts/check-live-api-smoke.ts`: Playwright smoke test for the hosted browser API.
- `scripts/postprocess-treeviz-export.py`: repeated SVG/PNG cleanup with Pillow
  and `rsvg-convert`.
- `scripts/reroot-newick-by-metadata.py`: repeatable Newick rerooting from TSV/CSV metadata.

## QA Rules

- Always `await` API calls before issuing dependent commands.
- Check `getDiagnostics()` after import and after major edits.
- Check `getRenderDiagnostics()` after a render when the renderer may omit an
  item, such as a connection with an unresolved endpoint.
- Check `getLayoutMetrics()` after layout changes.
- After restore, wait for `onReady` and `document.fonts.ready`, then wait until
  the camera and layout metrics stop changing across several animation frames.
  Confirm that exported SVG dimensions match the settled stage before saving a
  thumbnail.
- Judge legibility at the zoom the reader will use: labels hold their screen
  size above zoom 1, so `labelsVisible` and `labelsCulled` at fit differ from
  the counts at 2x. Call `view.zoom`, wait for the render, read the metrics again.
- Start layout QA with `contentOccupancyX`, `contentOccupancyY`,
  `labelsClipped`, `labelCollisions`, `trackDensity`, and `p75BranchPx`.
- Do not claim visual quality from configuration alone; inspect a recent screenshot, SVG, PNG, or PDF.
- For Python-generated sessions, run `validate_session(session)` and inspect `binding_diagnostics(session)`.
- Save final state as `.treeviz.json` when a user may need to reopen or revise the visualization.
