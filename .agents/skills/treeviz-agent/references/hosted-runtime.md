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
`.treeviz.json` files. The example manifest lists visible sessions,
thumbnails, counts, and provenance. File URL fields appear only for files that
are published with a session.

Do not infer browser support from the published Python package. The hosted app
and its schemas can be newer than `treeviz-phylo`.

## Example Catalog

Read `/examples/manifest.json` for the current sessions, their `sessionUrl`
values, and their provenance. The catalog includes:

- **Example 1: Mirusviricota**: a circular Extended Data Figure 9 tree with
  1,204 tips, 18 metadata tracks, and a fitted circular opening. Source:
  [doi:10.1038/s41564-025-02190-6](https://doi.org/10.1038/s41564-025-02190-6).
- **Example 2: SILVA taxonomy**: the upper-left SILVA **Whole database** panel
  of Figure 4 with 3,843 taxa, 3,257 leaves, 513,121 bacterial 16S sequences,
  imported node angles, count-scaled nodes and branches, 50 centered labels,
  and a continuous count legend. Source:
  [doi:10.1371/journal.pcbi.1005404](https://doi.org/10.1371/journal.pcbi.1005404).
- **Example 3: TARA Oceans Metazoa**
  ([figure](https://doi.org/10.1371/journal.pcbi.1005404.g003)): 550 taxa,
  including 275 terminal taxa, 20,212 OTUs, 250,296,231 reads, 73 labels,
  imported radial X/Y coordinates, and separate percentage/count axes. It uses
  real source data. Its display geometry was reconstructed and aligned to the
  paper raster because the original force-layout coordinates are unavailable.
- **Example 4** ([source](https://doi.org/10.1038/nature13805)): the published
  178-tip source topology and branch agreement. Its pairwise transfer weights
  are explicitly synthetic because the source has no recoverable transfer
  matrix.
- **Example 5** ([source](https://doi.org/10.1038/nmicrobiol.2016.48)): the
  published 3,083-tip tree of life with reconstructed radial positions and
  clade backgrounds.
- **Example 6** ([source](https://doi.org/10.1038/s41467-024-49644-9)): a
  rectangular 3,128-tip *S. aureus* CC398 reconstruction with Supplementary
  Data 1 annotations. Its topology and drawing distances are approximate, one
  annotation match is inferred, and the original dated tree file was not found.
- **Examples 7–9**: a [PhyloPhlAn source backbone](https://doi.org/10.1038/ncomms3304),
  [bioreactor MAGs](https://doi.org/10.1038/s41522-025-00679-w) with
  vector-derived heatmap colors, and an
  [HMP/MetaHIT taxonomic cladogram](https://doi.org/10.1038/nmeth.2066).

Read each provenance audit before reusing reconstructed geometry or derived
annotations.

Open the first two saved sessions with (the manifest's `sessionUrl` gives the rest):

```text
https://treeviz.newlineages.com/?session=/examples/example-1-mirusviricota/session.treeviz.json
https://treeviz.newlineages.com/?session=/examples/example-2-silva/session.treeviz.json
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
