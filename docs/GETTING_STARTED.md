# Getting Started

This page takes one hosted example to an exported PNG in the browser. No
install is needed. The Python and agent routes follow at the end.

## 1. Open an example

[Open the labelled tree of life](https://treeviz.newlineages.com/?session=/sessions/rekhatree-tol-phyla-labelled.treeviz.json).
It loads a 1070-genome tree whose phyla are collapsed to wedges.

The toolbar switches layout (**Rect**, **Circular**, **Radial**), toggles
branch lengths (phylogram or cladogram), and opens the **Controls**, **Tracks**,
**Legend** and **Export** panels. **Fit** resets the camera. The **Legend**
panel lists this session's three legends; the same legends sit in the figure.

## 2. Zoom in and hover

At the fitted view some phylum labels are missing: labels that would overlap
are culled. Scroll to zoom in on the bacterial fan. The labels keep their size
while the tree grows, and the culled ones return once they have room. Hover a
wedge: the tooltip gives the phylum, its leaf count, the branch length and the
node's attributes, with a swatch for each colour. Press `F` or click **Fit** to
return.

## 3. Find a phylum

Type `Cyanobacteriota` into **Search taxa and clades…** and press **Enter**.
The view zooms to the wedge. A search for a genome inside a collapsed phylum
lands on that phylum's wedge. **Shift+Enter** and the arrow keys step through
several hits; **Escape** clears the search.

## 4. Change what the wedges show

Open **Controls** and find the collapsed-wedge settings:

- **Size by** shows `pd`, the phylogenetic diversity stored on each phylum
  node, with **Size target** set to **Length**. Switch **Size by** to **Tree
  shape** to draw each wedge from the footprint of its collapsed subtree
  instead, then back to `pd`.
- **Fill** switches between **Background** (the enclosing clade background),
  **Branch** (the outline colour) and **Attribute** (a separate colour
  attribute chosen under **Fill attribute**).
- **Allow overlap** off, the default, keeps neighbouring wedges apart.
- **Collapsed wedge labels** is on **Leader lines** and **Collapsed wedge
  label direction** on **Along branch** in this session. Switch them to **At
  wedge tip** and **Outward** to seat every label at its wedge tip, reading
  out from the centre, then set them back.

Untick **Show labels** and **Show node circles** in the same panel to see the
figure without phylum names and isolate circles, then tick them again.

## 5. Recolour the branches

Still in **Controls**, **Colour branches by** has two groups. **Metadata
columns (scale)** maps a numeric table column onto a colour scale. **Node
colours (exact)** lists colourings stored on the tree itself, and this session
carries three: `vc` (domain), `mc` (a muted palette) and `cc` (a culturedness
gradient). Choose `cc`, then `vc` to return. Wedge outlines follow the branch
colour.

## 6. Look at the tree as a circle

Click **Circular**. Each leaf now gets an equal angular slot, so Archaea take
about a sixth of the ring, in proportion to their 182 of 1070 genomes. Click
**Radial** again: branches are drawn at their true lengths, and the longer
archaeal root-to-tip distances give that domain a larger footprint. The two
layouts encode different quantities.

## 7. Export

Open **Export**, choose **PNG**, and download. **SVG** gives an editable vector
file and **PDF** a printable page. **Sessions** saves a `.treeviz.json` that restores everything: tree,
edits, styling, and saved views.

## Next

- [Browser usage](BROWSER.md): load your own tree and metadata table.
- [Examples](EXAMPLES.md): the settings behind this figure and five others.
- [Python package](PYTHON.md): build sessions from scripts and notebooks.
- [Agent automation](AGENTS.md) and the [Browser API](API.md): drive the app
  through `window.__treeviz` with `?api=1`.
