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
`.treeviz.json` files. The example manifest lists current sessions, source
files, thumbnails, provenance, and synthetic-data labels.

Do not infer browser support from the published Python package. The hosted app
and its schemas can be newer than `treeviz-phylo`.

## Real-Data Sessions

Six hosted sessions hold a 1070-leaf GTDB marker tree with 84 collapsed phylum
clades in radial layout. Open one with `?session=`:

```text
https://treeviz.newlineages.com/?session=/sessions/rekhatree-tol-phyla.treeviz.json
```

- `rekhatree-tol-phyla`: domain branch colours, footprint wedges.
- `rekhatree-tol-phyla-pd`: wedge length from phylogenetic diversity, with
  `sizeScale: 'log'`, `sizeTarget: 'length'`, `sizeRange: [40, 400]`.
- `rekhatree-tol-phyla-cultured`: branches coloured by isolates per unit of
  diversity, wedges filled from the branch colour.
- `rekhatree-tol-phyla-muted`: muted branch colouring, footprint wedges.
- `rekhatree-tol-phyla-domain-cultured`: domain branch and outline colours with
  `fill: 'attribute'` from a second node-meta key at `fillOpacity: 0.85`.
- `rekhatree-tol-phyla-labelled`: phylum labels at the wedge tips and isolate
  circles, with `showLabels` and `showNodeCircles` on;
  `collapsedWedgeLabelDeclutter: true` with leader lines,
  `allowLabelOverlap: false`, three hand-written `legends` (Domain; Isolate
  genomes per phylum; Culturedness), `attributeLabels` for every node-meta
  key, and `figureLegendVisible: true`.

Read `getSession().view` after loading one to see the wedge options, node-meta
colour keys, and clade styles that produce the figure.

## Live API Smoke

When Playwright and Bun are available:

```bash
bun .agents/skills/treeviz-agent/scripts/check-live-api-smoke.ts \
  --url https://treeviz.newlineages.com/
```

When Playwright's bundled Chromium is unavailable, point the smoke at an
installed Chromium build:

```bash
TREEVIZ_CHROMIUM_EXECUTABLE_PATH=/path/to/chromium \
  bun .agents/skills/treeviz-agent/scripts/check-live-api-smoke.ts \
  --url https://treeviz.newlineages.com/
```

The smoke test opens the hosted app with `?api=1`, imports a small Newick tree,
plans and imports metadata, creates tracks, checks diagnostics, and verifies
that SVG export returns non-empty output. The custom domain injects a Cloudflare
Analytics beacon that TreeViz's self-only content security policy blocks. The
smoke ignores only that exact blocked-beacon message; other console errors
still fail the run.
