---
name: treeviz-agent
description: Use for agent-driven phylogenetic tree visualization in TreeViz: load Newick/Nexus/.treeviz.json sessions, import metadata, choose row keys, plan tracks, style clades, tune rectangular/circular layouts, inspect diagnostics, and export figures through the hosted TreeViz browser API.
---

# TreeViz Agent

TreeViz is a browser-based tree visualization tool. Keep biological reasoning,
file preparation, and interpretation in the agent; use TreeViz for deterministic
parsing, metadata binding, layout, styling, diagnostics, and export.

Default runtime:

```text
https://treeviz.newlineages.com/?api=1
```

Headless runtime for browser automation:

```text
https://treeviz.newlineages.com/?mode=headless&api=1
```

This public skill does not vendor the TreeViz browser app or frontend source.
Use the hosted app unless the user explicitly provides another TreeViz runtime.

## Core Workflow

1. Open TreeViz with `?api=1` and wait for `window.__treeviz`.
2. Import a tree or restore a `.treeviz.json` session.
3. Inspect `getSession()`, `commands()`, and `getDiagnostics()`.
4. For metadata, call `planMetadataImport(source, format, prompt)` before import.
5. Import metadata with the suggested row key, flags, and leaf identifier source.
6. Add or update tracks through `track.add`, `track.update`, and `track.reorder`.
7. Tune layout with `view.set-layout`, spacing, scale, labels, and legend commands.
8. Re-check diagnostics and layout metrics after each logical batch.
9. Export evidence: `.treeviz.json` for state, SVG/PNG/PDF for figures, and screenshots when visual quality is the claim.

## Visualization Defaults

- Start metadata-heavy figures in rectangular layout.
- Try circular or radial layout only when labels and metadata remain readable.
- Keep metadata tracks contiguous; use `metadataGap: 0` unless separation is useful.
- Reduce whitespace by tuning branch scale, leaf spacing, metadata scale, metadata gap, label size, and export cropping before enlarging the canvas.
- Use `binary-dots` tracks for leaf symbols such as presence/absence markers.
- Use support labels and internal-node markers for branch support when the tree carries numeric internal-node labels.
- Use exact style attributes for data-defined node circles and branch
  width/color; enable pretty terminal branches when the user asks for styled
  leaf-facing terminal branches.
- For one-off webapp edits, use Controls > Exact styling for data attributes,
  Style clade for clade branch/label styling, and Inspector for direct
  selected-node circle diameter/color and branch width/color.
- Use explicit legend titles and item labels when exporting publication figures.
- Treat high unmatched-leaf or unmatched-row counts as a binding problem to fix or report.

## Reference Loading

Load only the reference needed for the task:

- `references/browser-api.md`: hosted browser API methods, command ids, exact
  node/branch style commands, and JavaScript examples.
- `references/session-workflows.md`: metadata import, session review, clade resolution, and command mapping.
- `references/render-qa.md`: layout tuning, whitespace checks, screenshots, and export QA.
- `references/example-inputs.md`: deterministic 30-leaf and 100-leaf example recipes with metadata and support markers.
- `references/large-taxonomy-trees.md`: large taxonomy-tree workflows, metadata-derived categories, rerooting, and dense exports.
- `references/hosted-runtime.md`: hosted URLs, public machine-readable files, and live API smoke testing.
- `references/wrapper-api.md`: Python package and notebook workflows.

## Helper Scripts

- `scripts/check-live-api-smoke.ts`: Playwright smoke test for the hosted browser API.
- `scripts/postprocess-treeviz-export.py`: repeated SVG/PNG cleanup for exported figures.
- `scripts/reroot-newick-by-metadata.py`: repeatable Newick rerooting from TSV/CSV metadata.

## QA Rules

- Always `await` API calls before issuing dependent commands.
- Check `getDiagnostics()` after import and after major edits.
- Check `getLayoutMetrics()` after layout changes.
- Do not claim visual quality from configuration alone; inspect a recent screenshot, SVG, PNG, or PDF.
- For Python-generated sessions, run `validate_session(session)` and inspect `binding_diagnostics(session)`.
- Save final state as `.treeviz.json` when a user may need to reopen or revise the visualization.

## Read Next

- `references/session-workflows.md`
- `references/browser-api.md`
- `references/render-qa.md`
- `references/example-inputs.md`
- `references/wrapper-api.md`
