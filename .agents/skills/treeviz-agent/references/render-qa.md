# TreeViz Render QA

Use this reference for dense layouts, visual polish, and exported figures.

## QA Loop

1. Apply one logical batch of changes.
2. Read `getDiagnostics()`.
3. Read `getLayoutMetrics()`.
4. Capture a screenshot or export SVG, PNG, or PDF.
5. Inspect clipping, collisions, whitespace, legend placement, and track
   readability.
6. Adjust and render again when the evidence still shows a problem.

Do not claim visual quality from configuration alone.

## Current Layout Metrics

Start with:

- `contentOccupancyX` and `contentOccupancyY`: fraction of usable canvas covered
  by painted content. Values below about 0.7 can indicate recoverable whitespace.
- `labelsClipped`: labels that cross a viewport edge. The target is zero.
- `labelCollisions`: pairs of labels whose glyphs overlap, even when overlap is
  allowed.
- `labelsVisible` and `labelsCulled`: labels drawn and labels dropped by the
  overlap culler (`allowLabelOverlap: false`), at the current camera.
- `trackDensity`: metadata-lane density.
- `p75BranchPx`: branch-length measure that is less sensitive to one long
  branch. More than 160 px on an 8-to-100-tip tree often means the topology is
  stretched.
- `warnings`: metric warnings such as low occupancy or heavy label overlap.

Rectangular occupancy uses each viewport axis. Circular and radial occupancy
uses the shorter viewport side for both axes because the figure is round.

## Layout Rules

- Keep `branchScaleMode` on `auto` unless the user needs fixed geometry.
- Calling `view.set-branch-scale` switches the view to manual scale.
- Keep metadata tracks contiguous with `metadataGap: 0` unless separation has a
  clear purpose.
- Start metadata-heavy figures in rectangular layout.
- Try circular or radial layout only when labels, wedges, and legends remain
  readable.
- In radial, after collapsing many clades, check that wedges do not overlap
  (`collapsedWedgeAllowOverlap` is false by default) and that clade labels sit
  outside the wedge tips. Prefer `sizeTarget: 'length'` for data-sized wedges
  in a crowded fan. The crowding pass compares every pair of collapsed
  wedges, so a figure with hundreds of them renders slower.
- When wedge labels share a bearing, set `collapsedWedgeLabelDeclutter: true`
  (labels stack outward with leader lines) and `allowLabelOverlap: false`
  (labels that still collide are culled until the reader zooms in).
- Tighten leaf spacing only while labels and symbols remain distinct.
- Fix clipping with layout, font size, overlap policy, and track density before
  adding large margins.
- Keep scale bars clear of labels, branches, and tracks.
- Use `categoryColors` when exact categorical colors must survive upload.

## Legibility At A Zoom

Labels, strokes and node marks keep their screen size above zoom 1, so a
figure that culls labels at fit shows more of them at 2x. Metrics describe the
camera they were measured at:

```js
const atFit = api.getLayoutMetrics()
await api.execute('view.zoom', { factor: 2 })
// the culler re-runs ~150 ms after the camera settles
const atTwo = api.getLayoutMetrics()
```

Compare `labelsVisible`, `labelsCulled`, `labelCollisions` and `warnings`
between the two. On a small viewport the fitted zoom can be below 1; labels
then shrink with the tree; zoom in, or export at a larger canvas.

## Hosted Browser Evidence

Open the app with `?api=1`, make the final change, then collect:

```js
const evidence = {
  diagnostics: window.__treeviz.getDiagnostics(),
  metrics: window.__treeviz.getLayoutMetrics(),
  svg: window.__treeviz.exportSvg()
}
```

Capture a screenshot after this call. If the user will reopen the result, save
the same state as `.treeviz.json`.

## Export Cleanup

For repeated SVG and PNG cleanup:

```bash
uv run --with pillow python \
  .agents/skills/treeviz-agent/scripts/postprocess-treeviz-export.py \
  --svg results/tree.svg \
  --png results/tree.png \
  --layout circular
```

The helper also requires `rsvg-convert` on `PATH`.

The helper can remove a scale-bar layer, crop to rendered content, regenerate
an opaque PNG, and create dark copies. Use only the options needed by the
requested output.

## Final Checklist

- Diagnostics contain no unresolved errors relevant to the requested figure.
- `labelsClipped` is zero.
- Occupancy uses the available canvas; any remaining gap has a named cause.
- Label collisions and track density are acceptable for the requested layout.
- The latest screenshot or export was inspected after the final change.
- The saved session contains the requested tree edits, metadata, bindings,
  tracks, node marks, connections, view settings, and saved views.
- The exact `.treeviz.json` intended for upload opens in the hosted app.
