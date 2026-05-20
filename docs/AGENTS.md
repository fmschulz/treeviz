# Agent Automation

Agents should control TreeViz through `window.__treeviz` when the app is opened
with `?api=1`. This is more reliable than replaying clicks or guessing DOM
state.

## Runtime

Use the hosted app:

```text
https://treeviz.newlineages.com/?api=1
```

Use headless mode for render-only browser automation:

```text
https://treeviz.newlineages.com/?mode=headless&api=1
```

The public skill is available at:

```text
.agents/skills/treeviz-agent/SKILL.md
```

The skill does not include a browser build. It uses the hosted TreeViz app and
small helper scripts for session QA and file processing.

## Standard Sequence

```js
const api = window.__treeviz

await api.execute('session.import-tree', {
  source: '(A,B,(C,D));',
  name: 'example.nwk',
  format: 'newick'
})

const metadataText = [
  'id\tgroup\tvalue',
  'A\talpha\t1.2',
  'B\talpha\t0.8',
  'C\tbeta\t2.1',
  'D\tbeta\t1.6'
].join('\n')

const plan = api.planMetadataImport(metadataText, 'tsv', 'color by group and value')
if (!plan) throw new Error('metadata planning failed')

await api.execute('session.import-metadata', {
  source: metadataText,
  format: 'tsv',
  rowKeyColumn: plan.suggestedBinding.rowKeyColumn,
  flags: plan.suggestedBinding.flags,
  leafIdentifierSource: plan.suggestedBinding.leafIdentifierSource
})

await api.applyTrackRecommendations(plan.recommendedTracks)

const diagnostics = api.getDiagnostics()
const metrics = api.getLayoutMetrics()
const svg = api.exportSvg()
```

Check diagnostics after each logical batch. Treat error-level diagnostics as a
failed automation step unless the task intentionally tests invalid input.

## Practical Rules

- Load or restore a session before metadata, tracks, or styling.
- Use `commands()` when exact command ids or argument schemas matter.
- Use `planMetadataImport(...)` before importing metadata from text.
- Use stable keys from the session tree for clade edits.
- Use `view.set-tree-style-attributes` for exact node-circle and branch
  width/color values, and `view.set-pretty-terminal-branches` for styled
  terminal leaf branches.
- Re-check `getDiagnostics()` and `getLayoutMetrics()` after visual changes.
- Capture or export a figure after the final layout change before reporting that the figure is ready.
- Save durable work as `.treeviz.json`.

## References

- [Browser API](API.md)
- [Metadata](METADATA.md)
- [Tree styling](STYLING.md)
- [Exports](EXPORTS.md)
- [Troubleshooting](TROUBLESHOOTING.md)
