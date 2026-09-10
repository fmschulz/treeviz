# Examples

The visible catalog contains saved TreeViz sessions. Open one to inspect its
tree, metadata binding, tracks, view, and diagnostics. The [live
manifest](https://treeviz.newlineages.com/examples/manifest.json) is the
machine-readable catalog.

## Example 1: Mirusviricota

**Sourced data · 1,204 tips · 18 metadata tracks · circular tree**

[![Circular Mirusviricota phylogeny with 18 metadata tracks](assets/gallery/example-1-mirusviricota.svg){ loading=lazy }](https://treeviz.newlineages.com/?session=/examples/example-1-mirusviricota/session.treeviz.json)

This is the saved TreeViz view of the Mirusviricota phylogeny from Extended
Data Figure 9 in
[doi:10.1038/s41564-025-02190-6](https://doi.org/10.1038/s41564-025-02190-6).
Its fitted circular opening keeps the metadata track names visible.

[Open in TreeViz](https://treeviz.newlineages.com/?session=/examples/example-1-mirusviricota/session.treeviz.json) ·
[SVG figure](assets/gallery/example-1-mirusviricota.svg) ·
[Source paper](https://doi.org/10.1038/s41564-025-02190-6)

## Example 2: SILVA taxonomy

**Sourced data · 3,843 taxa · 3,257 leaves · 513,121 bacterial 16S sequences · circular taxonomy**

[![SILVA taxonomy with sequence-count-scaled nodes, branches, and selected taxon labels](assets/gallery/example-2-silva.svg){ loading=lazy }](https://treeviz.newlineages.com/?session=/examples/example-2-silva/session.treeviz.json)

This saved view reconstructs the upper-left SILVA **Whole database** panel of
Figure 4 from
[Foster et al.](https://doi.org/10.1371/journal.pcbi.1005404), using the SILVA
123.1 taxonomy. Node diameters, branch widths, and colors encode the 513,121
bacterial 16S sequences assigned across the taxonomy. The view labels 50
selected taxa.

Branch depth counts steps through the taxonomy. Circular
angles were reconstructed with the historical igraph 1.0.1 layout algorithm
used by the source workflow. They were not measured from the saved 2017 plot.

[Open in TreeViz](https://treeviz.newlineages.com/?session=/examples/example-2-silva/session.treeviz.json) ·
[SVG figure](assets/gallery/example-2-silva.svg) ·
[Source paper](https://doi.org/10.1371/journal.pcbi.1005404)
