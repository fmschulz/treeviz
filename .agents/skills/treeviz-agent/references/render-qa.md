# Render QA

Use this reference when the user asks for visual polish, dense tree layout,
exported figures, or proof that edits display correctly.

## QA Loop

Do not assume the first layout is good.

1. Apply one logical batch of changes.
2. Read `getDiagnostics()`.
3. Read `getLayoutMetrics()`.
4. Export SVG or capture a screenshot.
5. Inspect the latest output for clipping, collisions, whitespace, legend
   placement, and metadata readability.
6. Adjust and render again if needed.

Do not report that a figure looks good unless the latest rendered evidence was
inspected after the final layout change.

## Layout Heuristics

- Minimize whitespace first; dense, readable trees are usually preferable to
  wide empty margins.
- Keep metadata tracks contiguous with `metadataGap: 0` unless separation is
  useful.
- In rectangular layout, reduce branch scale before widening the canvas.
- Keep leaf spacing as tight as readability allows.
- If metadata dominates the figure, start in rectangular layout.
- Try circular or radial layout only when labels, metadata wedges, and legends
  remain readable.
- Keep the scale bar close to the tree but away from labels, tracks, and
  branches.
- Avoid solving clip or collision issues by adding large empty margins. Try
  font size, overlap policy, branch scale, leaf spacing, and track density
  first.

## Whitespace And Cropping

For Python static export, use:

```python
render_tree(
    tree,
    metadata=metadata,
    tracks=tracks,
    format="png",
    output="tree.png",
    command=["treeviz", "render"],
    auto_crop=True,
    crop_padding=24,
    metrics="tree.metrics.json",
)
```

Check the metrics JSON for large whitespace margins, low fill ratios, or crop
warnings.

For repeated SVG/PNG cleanup:

```bash
python .agents/skills/treeviz-agent/scripts/postprocess-treeviz-export.py \
  --svg results/tree.svg \
  --png results/tree.png \
  --layout circular
```

## Validation Checklist

- `getDiagnostics()` has no unresolved parse, binding, edit, or render errors.
- `getLayoutMetrics()` has no unresolved density, clipping, or collision issue
  relevant to the user request.
- The latest screenshot, SVG, PNG, or PDF was inspected after the most recent
  tuning pass.
- The saved `.treeviz.json` contains the tree edits, metadata, bindings,
  tracks, view settings, and saved views the user asked to preserve.
- Exported figure margins are tight enough and the figure is not clipped.
