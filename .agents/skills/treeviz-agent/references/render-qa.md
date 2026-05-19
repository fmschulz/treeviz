# TreeViz Render QA

Use this reference when the user asks for visual polish, dense tree layout, exported figures, or proof that edits display correctly.

## Render QA Loop

Do not assume the first layout is good. Iterate with render evidence:

1. Apply one logical batch of changes.
2. Read `getLayoutMetrics()`:
   - high `trackDensity` means metadata lanes are too wide or too numerous
   - non-zero `labelsClipped` or large `labelCollisions` means the view needs adjustment
   - unusually large `averageBranchPx` in rectangular mode often means the tree is too stretched horizontally
3. Capture a PNG or screenshot:
   - browser-driven flow: screenshot `[data-tv-id="tree-canvas.container"]`
   - file-driven flow: `bun run treeviz render <session-or-config> --output /tmp/treeviz-pass.png --format png`
4. Compare against the user's explicit aesthetic rules.
5. Adjust and render again.

Do not claim the layout is improved unless you have recent render evidence.

When using `bun run treeviz render` for multiple session files, run the commands sequentially. The CLI writes a shared `dist/__treeviz_compiled_session.json`; parallel renders can race and export the wrong session.

## Layout Heuristics

Use these defaults unless the user asked for a different visual style:

- Minimize whitespace first. Dense, readable trees are usually preferred over decorative breathing room.
- Keep metadata tracks contiguous. Set `metadataGap` to `0` or very close to it unless separation is explicitly useful.
- In rectangular layouts, keep branches relatively short before widening the canvas. Lower `branchScale` first.
- Keep leaf spacing as tight as readability allows. Increase only when labels or symbols genuinely collide.
- If metadata dominates the figure, rectangular is usually the best starting layout. Re-check circular/radial only if the track stack stays readable.
- Keep the scale bar close to the tree but never overlapping labels, tracks, or branches.
- Re-render after moving the scale bar or after any major spacing/layout change.
- Avoid solving clip/collision problems by adding large empty margins. First try font size, overlap policy, branch scale, leaf spacing, and track density.
- Circular phylograms emit a scale-bar layer whenever branch lengths are shown. If the final figure should have no scale bar, remove the SVG layer `data-tv-layer="scale-bar"` and rasterize the cleaned SVG.
- For no-label circular trees, use real branch lengths only when the user wants branch-length geometry; it removes forced tip-alignment spokes to metadata wedges but can need a larger canvas or smaller `branchScale` after rerooting.
- In dark exports, do not force default/reference branches to black in the config. TreeViz dark mode remaps default `#333333` tree strokes to light branches; explicit query/accent branch colors remain fixed.
- Fill intentional "not in focus" metadata track cells with an explicit category such as `other_reference` instead of leaving them missing. Missing colors are easy to mistake for label gaps or rendering errors.
- For `.treeviz.json` files meant to be uploaded to a hosted TreeViz deployment,
  use `categoryColors` on `color-strip` tracks for exact category hex colors.
  Match branch-rule colors to those explicit category colors instead of relying
  on first-seen palette slots.

## Export Cleanup

Use `scripts/postprocess-treeviz-export.py` for repeated cleanup:

```bash
python .agents/skills/treeviz-agent/scripts/postprocess-treeviz-export.py \
  --svg results/tree.svg \
  --png results/tree.png \
  --layout circular \
  --dark-copy
```

The script removes scale-bar layers, crops the SVG viewBox from raster content, regenerates an opaque white PNG, and optionally writes `_dark.svg` / `_dark.png` copies using TreeViz's dark-mode branch color remap.

## Validation Checklist

- `getDiagnostics()` has no unresolved parse, binding, edit, or render errors.
- `getLayoutMetrics()` has no unresolved density, clipping, or collision issues for the user's goal.
- The latest screenshot or PNG was inspected after the most recent tuning pass.
- The saved `.treeviz.json` still contains the tree edits, metadata, bindings, tracks, view settings, and saved views the user asked to preserve.
- For file exports, inspect PNG dimensions and content margins after post-processing; a visually blank quadrant usually means the tree was clipped before cropping, not that cropping failed.
- For uploadable JSON, open or otherwise validate the same `.treeviz.json` that the user will upload, not only post-processed PNG/SVG artifacts.
