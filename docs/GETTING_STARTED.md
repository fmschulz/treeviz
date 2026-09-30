# Getting started

This tutorial opens a sourced Mirusviricota tree, inspects its metadata tracks
and fitted circular layout, and exports a figure. It runs in the hosted browser
app and requires no installation.

## 1. Open the example

[Open Example 1: Mirusviricota](https://treeviz.newlineages.com/?session=/examples/example-1-mirusviricota/session.treeviz.json).
The saved Extended Data Figure 9 session contains 1,204 tips and 18 metadata
tracks. See the
[source paper](https://doi.org/10.1038/s41564-025-02190-6) for the biological
context.

## 2. Check the metadata tracks

Open **Tracks** to see every track listed by title. Expanding a track shows its
source column, palette, and width. As you zoom or pan, the rings keep their
alignment with the terminal tips.

## 3. Inspect the tree

Hovering over a tip shows its name, branch length, support value, and any
attributes stored on the tree node. Values from the metadata table appear in the
tracks rather than in the tooltip. To focus a named tip or clade, use search.
Press **Escape** to clear the search and **F** to fit the whole tree.

## 4. Inspect the fitted opening

Under **Controls**, open **Layout**. The opening in the circular layout makes
room for the horizontal track names. With **Auto-fit to labels**, the opening is
recalculated whenever the track names, visible tracks, ring widths, or viewport
change. Zooming and panning leave the fitted opening as it is.

Turning on **Tip-to-track guides** draws guides from terminal tips to the inner
metadata edge. Leave it off if the tracks are already easy to follow.
The fill colors for the opening and the interior sit under **Layout** as well.

## 5. Export or save

Open **Export** and choose an action:

- **Export SVG** for an editable vector figure.
- **Export PNG (N DPI)** for a raster image at the selected resolution.
- **Export PDF** for a printable page.
- **Export Session (JSON)** to preserve the tree, metadata, tracks, edits, view
  settings, and saved views.

The **Data** section exports the tree as Newick or Nexus, the leaf names, and
the metadata table as TSV.

The `.treeviz.json` session is the editable TreeViz record. Figure exports do
not preserve the interactive state.

## Continue with your data

- [Browser app](BROWSER.md): load a tree and metadata table from your computer.
- [Metadata](METADATA.md): choose a row key and handle unmatched rows or leaves.
- [Examples](EXAMPLES.md): inspect the hosted example and its provenance.
- [Python package](PYTHON.md): build sessions from scripts and notebooks.
- [Agent automation](AGENTS.md): control TreeViz through `window.__treeviz`.
