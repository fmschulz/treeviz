# Example Inputs

Use these deterministic examples when an agent needs a known-good TreeViz
session for testing metadata binding, tracks, support markers, legends, and
layout tuning.

The runnable source is:

```text
examples/plot_treeviz_examples.py
```

Run:

```bash
python examples/plot_treeviz_examples.py --out treeviz-example-output
```

## `lineage_30`

- 30 leaves named `L01` through `L30`.
- Rectangular layout.
- Leaf labels shown.
- Numeric internal-node labels provide support values.
- Metadata tracks:
  - clade color strip;
  - region color strip;
  - abundance gradient;
  - two-column score heatmap;
  - collection-day bar track;
  - binary marker dots as leaf symbols;
  - status text track.

Use this when testing labels, compact rectangular spacing, metadata alignment,
legend readability, and branch-support marker display.

## `clade_100`

- 100 leaves named `C001` through `C100`.
- Circular layout.
- Leaf labels hidden by default.
- Numeric internal-node labels provide support values.
- Metadata tracks:
  - clade color strip;
  - region color strip;
  - abundance gradient;
  - two-column score heatmap;
  - collection-day bar track;
  - binary marker dots as leaf symbols.

Use this when testing dense circular rendering, metadata wedges, support
markers, whitespace cropping, and summary figures.

## Bare Variants

The script also writes:

- `lineage_30_bare.treeviz.json`
- `clade_100_bare.treeviz.json`

Use the bare variants to compare tree layout with and without metadata tracks.

## Static Rendering

Static rendering is disabled by default. If a renderer command is available:

```bash
python examples/plot_treeviz_examples.py \
  --out treeviz-example-output \
  --render \
  --renderer-command treeviz render
```

The script writes SVG, PNG, PDF, crop metrics, and `summary.json`.
