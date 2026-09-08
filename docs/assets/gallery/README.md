# Gallery provenance

The ten catalog SVGs are TreeViz figure exports, not browser screenshots. They
include the tree, metadata tracks, and figure legends from the linked saved
sessions. Open the session in TreeViz to inspect the inputs and settings.

## Current example catalog

The SVGs were exported on 2026-09-08 from a TreeViz 0.8.2 review build based on
source commit `b2a4d102bce6820154d71ded0602c5ce727b7890` plus the reviewed catalog
and interface changes for this documentation update. The review build was not
the hosted production build at export time.

Each session was loaded in API-enabled headless mode at 1440 x 1000 pixels.
Export waited for fonts, two animation frames, and a 350 ms render-settle
period. The SVG bounds were cropped to the figure content with 24 pixels of
padding on each side. The dimensions below are the resulting SVG `width` and
`height` attributes.

| Figure | Saved session | Data and source | SVG size (px) |
| --- | --- | --- | ---: |
| `bacterial-starter.svg` | `/examples/bacterial-starter/session.treeviz.json` | GTDB release R232 tree and taxonomy | 1432.42 x 1032 |
| `bacterial-encoding-showcase.svg` | `/examples/bacterial-encoding-showcase/session.treeviz.json` | GTDB R232 topology and taxonomy; deterministic synthetic quantitative and metabolic encodings | 1244 x 1024 |
| `differential-expression.svg` | `/examples/differential-expression/session.treeviz.json` | Designed 40-gene topology and generated expression values | 1281.406 x 1012 |
| `ancestral-state-pies.svg` | `/examples/ancestral-state-pies/session.treeviz.json` | Deterministic topology, leaf groups, and ancestral-state values | 1090.44 x 1032 |
| `hgt-connections.svg` | `/examples/hgt-connections/session.treeviz.json` | Generated topology, groups, and 40 transfer events | 1326 x 1032 |
| `genome-symbol-lanes.svg` | `/examples/genome-symbol-lanes/session.treeviz.json` | Familiar bacterial species labels; generated topology and track values | 1120.665 x 660.527 |
| `large-bacterial-tree.svg` | `/examples/large-bacterial-tree/session.treeviz.json` | Generated 6,000-tip stress fixture | 1244 x 1024 |
| `bootstrap-heatmap-taxonomy.svg` | `/examples/bootstrap-heatmap-taxonomy/session.treeviz.json` | Generated 100-tip topology, taxonomy, and environmental values | 1326 x 1032 |
| `agent-clade-playground.svg` | `/examples/agent-clade-playground/session.treeviz.json` | Generated 100-tip topology, taxonomy, and measurements | 1203.485 x 1031 |
| `gradient-node-branch-styling.svg` | `/examples/gradient-node-branch-styling/session.treeviz.json` | Generated nine-tip topology and styling values | 985.928 x 684.231 |

`large-bacterial-tree.svg` is 5,951,837 bytes. The gallery embeds
`large-bacterial-tree.png`, a native TreeViz PNG export at 908 x 641 pixels and
72 DPI, to avoid loading the full SVG while scrolling. The PNG is 655,814
bytes; the gallery also links the vector figure.

The [live example manifest](https://treeviz.newlineages.com/examples/manifest.json)
records each example's current source files, purpose, synthetic-data flag, and
hosted session path. A browser user can reproduce a figure by opening the
linked session and choosing **Export**.

## Tree-of-life case studies

These four PNGs come from collaboration figures based on a 1,070-genome
concatenated-marker tree. The underlying tree and per-phylum isolate and
diversity tables are not redistributed in this repository, so the images are
visual case studies rather than reproducible example datasets.

| Image | Hosted session | Data | App build at render time |
| --- | --- | --- | --- |
| `tree-of-life-phylum-wedges.png` | `/sessions/rekhatree-tol-phyla.treeviz.json` | 776 Bacteria, 182 Archaea, and 112 Eukaryota; 84 of 93 phylum-level blocks collapsed to wedges | 0.6.0 (`44db170`) |
| `tree-of-life-wedge-length-by-diversity.png` | `/sessions/rekhatree-tol-phyla-pd.treeviz.json` | Same tree; wedge length maps log10 total phylogenetic diversity | 0.6.0 (`44db170`) |
| `tree-of-life-domain-outlines-culturedness-fill.png` | `/sessions/rekhatree-tol-phyla-domain-cultured.treeviz.json` | Same tree; outlines show domain and fills show isolate genomes per unit of phylogenetic diversity | 0.6.0 (`44db170`) |
| `tree-of-life-labelled-phyla.png` | `/sessions/rekhatree-tol-phyla-labelled.treeviz.json` | Same tree; phylum labels, isolate-count circles, and three figure legends | 0.8.0 (`dfecf53`) |

## Superseded images

Two older images remain for links from prior documentation versions. They are
not used on the current gallery page:

- `circular-taxonomy-heatmap-rings.png`: TreeViz 0.7.0 (`f28d2dd`), synthetic
  100-tip feature fixture.
- `rectangular-heatmap-bar-axis.png`: TreeViz 0.7.0 (`f28d2dd`), synthetic
  eight-tip expression fixture. The current expression example has 40 genes.
