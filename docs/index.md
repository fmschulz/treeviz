# TreeViz

[![Live app](https://img.shields.io/badge/live-treeviz.newlineages.com-green)](https://treeviz.newlineages.com){ .md-button }
[![GitHub](https://img.shields.io/badge/GitHub-fmschulz%2Ftreeviz-blue?logo=github)](https://github.com/fmschulz/treeviz){ .md-button }
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/fmschulz/treeviz/blob/main/LICENSE){ .md-button }

TreeViz is a client-side phylogenetic tree viewer and editor. It imports
Newick, CONTree, Nexus, metadata tables, and `.treeviz.json` sessions; renders
metadata tracks; supports common tree edits; and exports SVG, PNG, PDF, and
data files. Everything runs in the browser, with no server and no account.

This site covers the public browser app, the Python package, metadata
structure, tree styling, and agent automation.

The hosted app reports version 0.8.2. The Python examples target the released
`treeviz-phylo` 0.6.0 package. Its bundled schema lacks several fields the app
writes, so `validate_session` rejects app-saved sessions with them; see
[Schema Compatibility](PYTHON.md#schema-compatibility). Sessions from earlier
releases load and are migrated on open (see the layout note in
[Styling](STYLING.md#layouts)).

![Radial tree of life with phyla collapsed to wedges, coloured by domain](assets/gallery/tree-of-life-phylum-wedges.png)

*A 1070-genome tree of life with 84 phyla collapsed to wedges. Settings and session link on the [Examples](EXAMPLES.md) page.*

---

## What TreeViz does

| Surface | Purpose | Where to start |
| --- | --- | --- |
| **Browser app** | Load trees, add metadata tracks, edit clades, save and share sessions | [Browser app](BROWSER.md) |
| **Tree styling** | Map node circles, branch width/color, heatmaps, and terminal branches | [Tree styling](STYLING.md) |
| **Metadata** | Bind TSV/CSV tables to leaves by stable key, independent of leaf order | [Metadata](METADATA.md) |
| **Python package** | Build `.treeviz.json` sessions from scripts and notebooks | [Python package](PYTHON.md) |
| **Exports** | SVG, PNG, PDF, Newick, Nexus, leaf lists, metadata TSV, session JSON | [Exports](EXPORTS.md) |
| **Browser API** | Drive the app programmatically via `window.__treeviz` | [Browser API](API.md) |
| **Agent automation** | Control patterns for Codex, Claude Code, and similar agents | [Agent automation](AGENTS.md) |

---

## Start here

- [**Getting started**](GETTING_STARTED.md): one hosted example to an exported figure in the browser.
- [**Browser app**](BROWSER.md): load trees, add metadata, save sessions, export figures.
- [**Python package**](PYTHON.md): build `.treeviz.json` sessions from scripts and notebooks.
- [**Metadata**](METADATA.md): prepare TSV/CSV metadata and track definitions.
- [**Tree styling**](STYLING.md): node circles, branch width/color, pretty terminal branches.

## More

- [Examples](EXAMPLES.md): complete figures with their settings and hosted sessions.
- [Hosted examples](https://treeviz.newlineages.com/): open current biological,
  feature, and stress-test sessions.
- [Troubleshooting](TROUBLESHOOTING.md): resolve binding, display, and export issues.
- [GitHub repo](https://github.com/fmschulz/treeviz) · [Live app](https://treeviz.newlineages.com)

!!! note "Public scope"
    This repository is documentation-first. It does not vendor the TreeViz
    browser app, frontend source, deployment scripts, project planning notes,
    or generated build artifacts.
