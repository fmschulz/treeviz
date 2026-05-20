# Examples

The public examples show how to build TreeViz sessions from Python with
metadata, leaf symbols, branch-support markers, and layout presets.
The example script also demonstrates passing TreeViz view settings from Python,
including exact node/branch styling fields and `prettyTerminalBranches`.

## Python Script

Install the package:

```bash
pip install treeviz-phylo
```

Generate example sessions:

```bash
python examples/plot_treeviz_examples.py --out treeviz-example-output
```

The script writes:

- `lineage_30.treeviz.json`: a 30-leaf rectangular example with metadata tracks;
- `lineage_30_bare.treeviz.json`: the same tree without metadata;
- `clade_100.treeviz.json`: a 100-leaf circular example with metadata tracks;
- `clade_100_bare.treeviz.json`: the same tree without metadata;
- `summary.json`: leaf counts, tree statistics, binding diagnostics, and hosted URLs.

To render SVG, PNG, or PDF files, provide a renderer command:

```bash
python examples/plot_treeviz_examples.py \
  --out treeviz-example-output \
  --render \
  --renderer-command treeviz render
```

If no local renderer is available, open the generated `.treeviz.json` files in
the hosted browser app.

## Metadata Features Covered

The metadata examples include:

- exact leaf binding through a row-key column;
- categorical color strips;
- continuous gradients;
- heatmaps;
- bar tracks with axes;
- binary dot tracks for leaf symbols;
- text tracks;
- internal-node support labels and support markers;
- exact terminal-node circles, branch width/color, and pretty terminal branches;
- rectangular and circular layouts.

## Agent Skill Examples

Agents should read
[`example-inputs.md`](https://github.com/fmschulz/treeviz/blob/main/.agents/skills/treeviz-agent/references/example-inputs.md)
when they need deterministic 30-leaf or 100-leaf prompt examples.
