# Hosted Runtime

Use this reference when an agent needs to verify the public TreeViz runtime or
discover public machine-readable files.

## URLs

- App: `https://treeviz.newlineages.com/`
- API mode: `https://treeviz.newlineages.com/?api=1`
- Headless API mode: `https://treeviz.newlineages.com/?mode=headless&api=1`
- Compact agent entry: `https://treeviz.newlineages.com/agent`
- Agent guide: `https://fmschulz.github.io/treeviz/AGENTS/`
- Browser API reference: `https://fmschulz.github.io/treeviz/API/`

## Public Files

- `/version.json`
- `/treeviz-command-schema.json`
- `/treeviz-session.schema.json`
- `/examples/manifest.json`

Use the command schema to compare expected browser command ids with
`window.__treeviz.commands()`. Use the session schema to validate generated
`.treeviz.json` files. The example manifest lists the visible session, its
thumbnail, counts, and provenance. File URL fields appear only for files that
are published with the session.

Do not infer browser support from the published Python package. The hosted app
and its schemas can be newer than `treeviz-phylo`.

## Example Catalog

Read `/examples/manifest.json` for the current session and its provenance. It
contains one visible entry:

- **Example 1: Mirusviricota**: a fitted circular Extended Data Figure 9 tree
  with 1,204 tips and 18 metadata tracks. Source:
  [doi:10.1038/s41564-025-02190-6](https://doi.org/10.1038/s41564-025-02190-6).

Open the saved session with:

```text
https://treeviz.newlineages.com/?session=/examples/example-1-mirusviricota/session.treeviz.json
```

Use the manifest instead of assuming that separate tree, metadata, or TOML
files exist for a session.

## Live API Smoke

When Playwright and Bun are available, run this from the installed
`treeviz-agent` skill directory:

```bash
bun scripts/check-live-api-smoke.ts \
  --url https://treeviz.newlineages.com/
```

When Playwright's bundled Chromium is unavailable, point the smoke at an
installed Chromium build:

```bash
TREEVIZ_CHROMIUM_EXECUTABLE_PATH=/path/to/chromium \
  bun scripts/check-live-api-smoke.ts \
  --url https://treeviz.newlineages.com/
```

The smoke test opens the hosted app with `?api=1`, imports a small Newick tree,
plans and imports metadata, creates tracks, checks diagnostics, and verifies
that SVG export returns non-empty output. The custom domain injects a Cloudflare
Analytics beacon that TreeViz's self-only content security policy blocks. The
smoke ignores only that exact blocked-beacon message; other console errors
still fail the run.
