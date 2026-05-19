# Automate TreeViz With Agents

Agents should control TreeViz through `window.__treeviz` instead of DOM
gestures whenever the app is opened with `?api=1`.

## Runtime Order

1. Use `https://treeviz.newlineages.com/?api=1` for normal public workflows.
2. Use `https://treeviz.newlineages.com/?mode=headless&api=1` for render-only
   browser automation.
3. Use the bundled app launcher when data must stay local or a pinned app build
   is required:

   ```bash
   bun .agents/skills/treeviz-agent/scripts/launch-treeviz-app.ts --port 5174
   ```

4. Inspect source only for TreeViz development tasks.

## API Workflow

```js
const api = window.__treeviz

await api.execute('session.import-tree', {
  source: '(A,B,(C,D));',
  name: 'example.nwk'
})

const plan = api.planMetadataImport(metadataText, 'tsv', 'color by group')
await api.execute('session.import-metadata', {
  source: metadataText,
  format: 'tsv',
  rowKeyColumn: plan.suggestedBinding.rowKeyColumn,
  flags: plan.suggestedBinding.flags,
  leafIdentifierSource: plan.suggestedBinding.leafIdentifierSource
})

await api.applyTrackRecommendations(plan.recommendedTracks)
await api.execute('track.add', { kind: 'gradient', columnKey: 'value' })

const diagnostics = api.getDiagnostics()
const svg = api.exportSvg()
```

Check diagnostics after each logical batch. Treat error-level diagnostics as
failed automation unless the task intentionally tests an invalid input.

## References

- [API command surface](API.md)
- [Metadata rules](METADATA.md)
- Agent skill: `.agents/skills/treeviz-agent/SKILL.md`
