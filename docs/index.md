# TreeViz Wiki

TreeViz visualizes phylogenetic trees with metadata tracks, clade annotations,
layout controls, and browser-based export. This wiki covers the public app,
the Python package, metadata structure, and agent automation.

## Start Here

- [Getting started](GETTING_STARTED.md): choose the browser, Python, or agent workflow.
- [Browser usage](BROWSER.md): load trees, add metadata, save sessions, and export figures.
- [Python package](PYTHON.md): build `.treeviz.json` sessions from scripts and notebooks.
- [Metadata](METADATA.md): prepare TSV/CSV metadata and track definitions.
- [Tree styling](STYLING.md): map node circles, branch width/color, and pretty terminal branches.

## Workflows

- [Exports](EXPORTS.md): save sessions, SVG, PNG, PDF, Newick, Nexus, and metadata.
- [Examples](EXAMPLES.md): run the package example script and inspect generated sessions.
- [Troubleshooting](TROUBLESHOOTING.md): resolve binding, display, and export issues.

## Reference

- [Browser API](API.md): command ids and `window.__treeviz` methods for automation.
- [Agent automation](AGENTS.md): practical control pattern for Codex, Claude Code, and similar agents.
- [Example notes](examples/README.md): repository examples and notebook guidance.

## Public Scope

This repository is intentionally documentation-first. It does not vendor the
TreeViz browser app, frontend source, deployment scripts, project planning
notes, or generated build artifacts.
