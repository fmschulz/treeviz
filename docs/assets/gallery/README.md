# Gallery provenance

Every image in this folder is a `treeviz render` export of a session that is
hosted on the live app, so each one can be reopened, inspected and re-exported.
App version at render time: 0.8.0 (`version.json` commit `dfecf53`) for the
labelled tree-of-life image, 0.7.0 (`f28d2dd`) for the two synthetic
fixtures, and 0.6.0 (`44db170`) for the first three tree-of-life images.

| Image | Hosted session | Data |
| --- | --- | --- |
| `tree-of-life-phylum-wedges.png` | `/sessions/rekhatree-tol-phyla.treeviz.json` | GTDB concatenated-marker tree, 1070 genomes (776 Bacteria, 182 Archaea, 112 Eukaryota), 84 of 93 phylum-level blocks collapsed to wedges, single-genome phyla drawn as leaves |
| `tree-of-life-wedge-length-by-diversity.png` | `/sessions/rekhatree-tol-phyla-pd.treeviz.json` | same tree; wedge length maps log10 of each phylum's total phylogenetic diversity |
| `tree-of-life-domain-outlines-culturedness-fill.png` | `/sessions/rekhatree-tol-phyla-domain-cultured.treeviz.json` | same tree; outlines by domain, fills by isolate genomes per unit of diversity |
| `tree-of-life-labelled-phyla.png` | `/sessions/rekhatree-tol-phyla-labelled.treeviz.json` | same tree; phylum labels at wedge tips in their domain colour, decluttered with leader lines and culled where they still collide, isolate-count circles, three hand-written legends, Branch spacing 1.6 |
| `circular-taxonomy-heatmap-rings.png` | `/examples/bootstrap-heatmap-taxonomy/session.treeviz.json` | synthetic 100-tip fixture (feature demonstration) |
| `rectangular-heatmap-bar-axis.png` | `/examples/differential-expression/session.treeviz.json` | synthetic 8-tip fixture (feature demonstration) |

Render command, run from a TreeViz source checkout with the session file local:

```bash
bun run treeviz render <session>.treeviz.json --format png \
  --width 1600 --height 1600 --fit-canvas --crop-padding 20 -o <image>.png
```

The labelled tree-of-life figure is rendered at 2400 x 2400 so its phylum
labels stay legible. Without a source checkout, open the hosted session URL in
the browser and use Export > PNG.

The four tree-of-life sessions come from a collaboration figure. The tree and the
per-phylum isolate and diversity tables are not redistributed here. Only the
finished sessions are.
