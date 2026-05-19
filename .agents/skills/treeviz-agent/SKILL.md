---
name: treeviz-agent
description: Use for AI-agent-driven phylogenetic tree visualization in TreeViz: load Newick/Nexus/.treeviz.json sessions, import metadata, choose row keys and leaf identifiers, plan tracks, style clades, tune layouts, export figures, or control `window.__treeviz` in `?api=1` mode.
---

# TreeViz Agent

TreeViz is a deterministic rendering and editing engine. Keep the reasoning in
the agent, and drive TreeViz through its command/API surface instead of brittle
DOM gestures whenever `?api=1` is available. Use `?mode=headless&api=1` for
render-only QA.

Default hosted runtime:

```text
https://treeviz.newlineages.com/?api=1
https://treeviz.newlineages.com/?mode=headless&api=1
```

## Bundled App Launcher

Launch the precompiled TreeViz browser app without starting Vite:

```bash
bun .agents/skills/treeviz-agent/scripts/launch-treeviz-app.ts --port 5174
```

To open a saved session directly:

```bash
bun .agents/skills/treeviz-agent/scripts/launch-treeviz-app.ts \
  --session path/to/session.treeviz.json \
  --port 5174
```

The launcher serves `assets/treeviz-app.tar.gz` over localhost and opens a
`?api=1` URL. Use `--headless` for `?mode=headless&api=1`, and `--no-open`
when another process will connect to the printed URL.

Refresh the bundled app after source changes with:

```bash
bun run build
bun run package:app
```

## Core Workflow

1. Open or launch TreeViz with `?api=1`.
2. Load or restore the tree/session before metadata, tracks, or styling.
3. Inspect `getSession()`, `commands()`, and `getDiagnostics()` before each logical batch.
4. For metadata, call `planMetadataImport(source, format, prompt)` before `session.import-metadata`.
5. Execute exact command ids with stable keys through `execute(...)`.
6. Apply changes in small awaited batches, then re-check diagnostics and layout metrics.
7. Save durable work as `.treeviz.json` when tree edits, metadata, tracks, view settings, or saved views must persist.

## Visualization Defaults

- Prefer the metadata planner over re-deriving row-key, normalization, and track heuristics.
- Treat high unmatched-leaf or unmatched-row counts as a binding problem to explain or fix.
- Start dense metadata-heavy figures in rectangular layout. Try circular or radial only when the track stack and labels remain readable.
- Reduce whitespace by tuning `branchScale`, `leafSpacing`, `metadataScale`, `metadataGap`, and label size before enlarging the canvas.
- Keep metadata tracks contiguous; use `metadataGap: 0` or near-zero unless separation is explicitly useful.
- Use `categoryColors` on `color-strip` tracks when exact category hex colors must survive hosted uploads. Match branch-rule colors to the same hex values.
- For publication figures, put explanatory taxonomy or group colors into the figure legend with `view.set-figure-legend-section` and `view.set-panel-position`.
- For Jupyter/Python wrapper examples, pass the same `tracks` and `view` config to `build_session(...)` and `view_tree(...)`, call `display(view)`, and render a static PNG/SVG artifact for visual QA. On `nb.newlineages.com`, use the `Python (Pixi)` kernel.
- Keep manual control available: if the user asks for a plan before applying tracks, stop after presenting the plan.

## Reference Loading

Load details only when the task needs them:

- `references/browser-api.md`: exact API methods, command ids, JavaScript examples, and stable-key control.
- `references/session-workflows.md`: metadata import, existing-session metadata review, rebinding, and clade resolution.
- `references/render-qa.md`: visual polish, layout tuning, screenshots, exported PNG/SVG evidence, and post-processing.
- `references/large-taxonomy-trees.md`: large taxonomy trees, query/reference strips, metadata-driven rerooting, and publication exports.
- `references/release-deploy.md`: public artifacts, release checks, deployment smoke, and bundled app refresh.
- `references/wrapper-api.md`: TreeViz-native Python/R wrappers, Jupyter/R usage, and session validation.

## QA Rules

- Always `await` each API call before issuing the next one.
- Inspect `getDiagnostics()` and `getLayoutMetrics()` after the latest visual change.
- Capture a screenshot or exported PNG before claiming a layout or aesthetic improvement.
- For file-driven CLI exports, render one session at a time; the render command writes a shared bootstrap file under `dist/`.
- For broad feature audits, cover import, metadata, layouts, tracks, legends, diagnostics, saved views, selection/search/inspector, tree edits, exports, light/dark modes, and responsive states.

## Read Next

- `references/session-workflows.md`
- `references/large-taxonomy-trees.md`
- `references/browser-api.md`
- `references/render-qa.md`
- `references/release-deploy.md`
- `references/wrapper-api.md`
