# Release And Deployment

Use this reference when packaging, validating, or deploying TreeViz. Keep source
edits separate from release operations so generated artifacts can be reviewed
clearly.

## Public Runtime Contract

- App: `https://treeviz.newlineages.com/`
- API mode: `https://treeviz.newlineages.com/?api=1`
- Headless API mode:
  `https://treeviz.newlineages.com/?mode=headless&api=1`
- Agent docs page: `https://treeviz.newlineages.com/agent.html`

Build output must serve:

- `/version.json`
- `/treeviz-command-schema.json`
- `/treeviz-session.schema.json`
- `/examples/manifest.json`

## Local Release Gates

Run:

```bash
bun install
bun run ci
bun run build
bun run check:skill
bun run package:app
bun run check:release
```

`bun run ci` covers TypeScript, ESLint, dependency-cruiser, Vitest, and bundle
size. `check:skill` validates the agent skill layout. `check:release` verifies
generated public artifacts, version metadata, release docs, and the bundled app
manifest/archive.

## Bundled App Refresh

Refresh the skill bundle after behavior changes:

```bash
bun run build
bun run package:app
bun .agents/skills/treeviz-agent/scripts/check-bundled-app-smoke.ts
```

The smoke launches the precompiled app only; it does not use Vite or source
files. It must expose `window.__treeviz`, import a small Newick tree, report no
diagnostic errors, and export non-empty SVG.

## Deployment Smoke

After `bun run deploy:pages`, verify the custom domain:

```bash
bun .agents/skills/treeviz-agent/scripts/check-live-api-smoke.ts \
  --url https://treeviz.newlineages.com/
```

The smoke compares `window.__treeviz.commands()` with the published command
schema, imports a tree, plans/imports metadata, creates tracks, checks
diagnostics, and verifies SVG export.

Record the Cloudflare Pages preview URL, custom-domain HTTP status, and smoke
result in release notes or the task log.
