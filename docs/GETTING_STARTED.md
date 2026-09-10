# Getting Started

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

Open **Tracks**. Each track is listed by title. Expand a track to inspect its
source column, palette, and width. The rings stay aligned with the terminal tips
as you zoom or pan.

## 3. Inspect the tree

Hover a tip to read its name, branch length, and metadata values. Use search to
focus a named tip or clade. Press **Escape** to clear the search and **F** to fit
the whole tree.

## 4. Inspect the fitted opening

Open **Controls**, then **Layout**. The circular opening leaves space for the
horizontal track names. **Auto-fit to labels** recalculates the opening when
track names, visible tracks, ring widths, or the viewport change. Zoom and pan
do not change the fitted opening.

Turn **Tip-to-track guides** on to draw guides from terminal tips to the inner
metadata edge. Turn it off when the tracks are already easy to follow. Opening
and interior fill colors are also under **Layout**.

## 5. Export or save

Open **Export** and choose a format:

- **SVG** for an editable vector figure.
- **PNG** for a raster image.
- **PDF** for a printable page.
- **TreeViz session** to preserve the tree, metadata, tracks, edits, view
  settings, and saved views.

The `.treeviz.json` session is the editable TreeViz record. Figure exports do
not preserve the interactive state.

## Continue with your data

- [Browser app](BROWSER.md): load a tree and metadata table from your computer.
- [Metadata](METADATA.md): choose a row key and handle unmatched rows or leaves.
- [Examples](EXAMPLES.md): inspect the hosted example and its provenance.
- [Python package](PYTHON.md): build sessions from scripts and notebooks.
- [Agent automation](AGENTS.md): control TreeViz through `window.__treeviz`.
