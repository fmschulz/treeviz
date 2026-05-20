# Hosted Runtime

Use this reference when an agent needs to verify the public TreeViz runtime or
discover public machine-readable files.

## URLs

- App: `https://treeviz.newlineages.com/`
- API mode: `https://treeviz.newlineages.com/?api=1`
- Headless API mode: `https://treeviz.newlineages.com/?mode=headless&api=1`

## Public Files

- `/version.json`
- `/treeviz-command-schema.json`
- `/treeviz-session.schema.json`
- `/examples/manifest.json`

Use the command schema to compare expected browser command ids with
`window.__treeviz.commands()`. Use the session schema to validate generated
`.treeviz.json` files.

## Live API Smoke

When Playwright and Bun are available:

```bash
bun .agents/skills/treeviz-agent/scripts/check-live-api-smoke.ts \
  --url https://treeviz.newlineages.com/
```

The smoke test opens the hosted app with `?api=1`, imports a small Newick tree,
plans and imports metadata, creates tracks, checks diagnostics, and verifies
that SVG export returns non-empty output.
