# Getting Started

This tutorial opens a sourced bacterial tree, checks its metadata track,
compares two layouts, and exports a figure. It runs in the hosted browser app
and requires no installation.

## 1. Open the starter

[Open the Bacterial Diversity Starter](https://treeviz.newlineages.com/?session=/examples/bacterial-starter/session.treeviz.json).
The session contains 42 representative species from seven bacterial phyla. Its
tree and taxonomy derive from [GTDB release
R232](https://data.gtdb.ecogenomic.org/releases/release232/).

The saved session opens as a rectangular phylogram with leaf labels, branch
lengths, and one family track.

## 2. Check the metadata track

Open **Tracks**. Each track is listed by title. Expand **Family** to edit its
column, palette, and width; the first track is open when the panel appears. The
track reads the `family` column from the linked taxonomy table. TreeViz matches
rows to leaves by the `species` row key rather than table position.

You can inspect the exact inputs:

- [Newick tree](https://treeviz.newlineages.com/examples/bacterial-starter/tree.nwk)
- [TSV taxonomy](https://treeviz.newlineages.com/examples/bacterial-starter/metadata.tsv)
- [TOML configuration](https://treeviz.newlineages.com/examples/bacterial-starter/treeviz.toml)

## 3. Inspect a species

Hover a leaf to read its name, branch length, and metadata values. Search for
`Aquipseudomonas aylmerensis` to focus that tip. Press **Escape** to clear the
search and **F** to fit the whole tree.

## 4. Compare layouts

Switch from **Rectangular** to **Circular**, then press **F**. The same tree and
family values now fill a ring. Switch back to **Rectangular** to restore the
saved figure's layout.

Open **Controls** when you need more detail. Quick actions for label and
metadata-track visibility appear first. The settings are grouped under
**Layout**, **Labels**, **Branches & nodes**, and **Metadata**. The stage
toolbar holds the layout and branch-length buttons used in this tutorial.

## 5. Export or save

Open **Export** and choose the output that matches the next step:

- **SVG** for an editable vector figure.
- **PNG** for a raster image.
- **PDF** for a printable page.
- **TreeViz session** to preserve the tree, metadata, tracks, edits, and view settings.

The `.treeviz.json` session is the editable TreeViz record. Figure exports do
not preserve the interactive state.

## Continue with your data

- [Browser app](BROWSER.md): load a tree and metadata table from your computer.
- [Metadata](METADATA.md): choose a row key and handle unmatched rows or leaves.
- [Examples](EXAMPLES.md): compare the ten hosted example sessions and their data provenance.
- [Python package](PYTHON.md): build sessions from scripts and notebooks.
- [Agent automation](AGENTS.md): control TreeViz through `window.__treeviz`.
