# Agent-First Styling And Figure Goal

## Goal

Make TreeViz the most reliable way for coding agents and scientific users to
turn phylogenetic trees, metadata tables, and natural-language styling requests
into compact, publication-ready figures.

The core product direction is not just "more styling controls". The goal is a
small, precise styling system that agents can drive deterministically:

- curated palettes with clear rules for when to use them;
- compact color controls that always allow direct hex input and paste;
- metadata-driven conditional formatting for branches, nodes, labels, symbols,
  wedges, and metadata tracks;
- command/API, CLI, Python, R, and documentation examples that all describe the
  same behavior;
- screenshot-backed examples that show TreeViz can produce dense, beautiful
  tree figures with minimal whitespace.

## Assumptions

- This implementation repo remains the source of truth until the source code and
  public documentation are consolidated into one open-source repository.
- The public docs repo at `../treeviz` should receive mirrored documentation
  once the feature is implemented and the examples are verified.
- Browser-side TreeViz should not depend on Python plotting packages at runtime.
  Python, Matplotlib, and palette libraries may inform palette selection and
  wrapper examples, but the web app should ship a small static palette registry.
- The manuscript package currently lives outside this repo at
  `~/Documents/shared/manuscripts/treeviz`.
- Built-in language should focus on TreeViz capabilities and agent workflows,
  not comparison claims against another tool.

## Product Principles

- Prefer deterministic, inspectable outputs over opaque styling magic.
- Keep controls compact: swatches, icons, popovers, short labels, and direct hex
  fields instead of large always-visible color editors.
- Every visual mapping needs an equivalent session field or command path so an
  agent can generate the same figure without clicking through the UI.
- Styling should be data-driven first. Manual clade edits remain useful, but the
  main path should be metadata rules, saved presets, and reproducible configs.
- Documentation examples must be executable or easy to verify through
  `window.__treeviz`, TOML configs, or wrapper code.

## Scope

### 1. Palette Registry

Add a curated palette registry for the web app and wrappers.

Required palette roles:

- sequential: ordered positive values such as abundance, branch length, support,
  or intensity;
- diverging: centered values such as signed effect size, log fold-change, score
  difference, residuals, or normalized contrasts;
- categorical: unordered groups such as clade class, sample group, phenotype,
  domain, or environment;
- neutral: quiet grays and low-saturation palettes for context, hidden
  branches, secondary tracks, or de-emphasized labels.

Initial default candidates:

- sequential: `viridis`, `magma`, `cividis`, `blues`;
- diverging: blue-orange, purple-green, brown-teal, coolwarm-style;
- categorical: Okabe-Ito, Tableau 10, paired, muted;
- neutral: gray, slate, soft monochrome.

Each palette record should include:

- stable id;
- display label;
- role;
- colors;
- recommended use;
- warnings or limits, for example maximum categorical levels;
- colorblind-friendly flag when appropriate;
- source or inspiration note where needed.

The web app should expose palette selection in compact controls. The API,
session schema, CLI config, Python docs, R docs, and agent skill should all use
the same palette ids.

### 2. Compact Color Editing

Replace large color-selection surfaces in node, clade, and label editing with a
compact control pattern.

Required behavior:

- small visible swatch;
- direct hex field with paste support;
- validation for CSS hex and named colors where accepted;
- optional popover for palette colors and recent colors;
- keyboard-friendly commit and cancel behavior;
- no persistent panel that consumes excessive sidebar space.

Targets:

- label color edits;
- clade color edits;
- node color edits;
- branch color edits;
- track palette edits;
- legend color edits if applicable.

### 3. Conditional Styling Rules

Add a reusable rule model for metadata-driven formatting.

Rule types:

- exact category match;
- numeric interval;
- quantile or rank bin;
- missing-value condition;
- boolean condition;
- regex or text contains condition where useful.

Rule targets:

- branch color;
- branch width;
- terminal node color;
- terminal node size;
- internal split marker color or size;
- label color;
- label weight;
- label visibility;
- track bar color;
- track bar-to-symbol conversion;
- track bar-to-wedge conversion.

Rules should be saved in `.treeviz.json` sessions and should be constructible by
browser commands and TOML configs. Agents should be able to inspect active rules
through the browser API.

### 4. Track-To-Symbol And Track-To-Wedge Styling

Extend existing track behavior so numeric or categorical tracks can be rendered
as compact categorical symbols or wedges when bars take too much horizontal
space.

Required behavior:

- user-defined interval bins;
- automatic interval bins for quick use;
- category labels in legends;
- symbol choices such as circle, square, triangle, diamond, plus, and dash;
- colored wedge option for compact multi-state display;
- API and TOML representation for the same settings.

This should support common uses such as bootstrap/support bins, abundance bins,
phenotype categories, host categories, and quality tiers.

### 5. Agent-Oriented Natural-Language Workflows

TreeViz does not need to run an LLM internally. Instead, the app, wrappers, and
skill should make it easy for an external coding agent to translate a prompt
into deterministic commands.

Documentation should include 3-4 tested prompt examples, for example:

1. "Create a circular tree using a colorblind-safe categorical palette for
   phylum, make high-abundance leaves larger, show a compact legend, and export
   a tight PNG."
2. "Use a blue-orange diverging palette centered at zero for signed score,
   hide rows below the significance threshold, and export both SVG and the
   session JSON."
3. "Convert the abundance bar track into three symbol bins with intervals
   0-10, 10-50, and greater than 50, use hex #2563eb for query branches, and
   minimize whitespace."
4. "Style bootstrap support as internal split circles, use muted group colors
   for labels, collapse weakly supported clades, and export a manuscript-ready
   figure."

For each prompt, documentation should show:

- the resulting TreeViz command sequence or config;
- the expected visual intent;
- the generated example session path;
- at least one screenshot or export when the example is part of the screenshot
  set.

### 6. Example Sessions And Screenshots

Build several example sessions that demonstrate the visual system under real
constraints:

- dense tree with categorical metadata;
- circular layout with compact labels;
- diverging quantitative branch or node styling;
- bootstrap/support styling with symbols or internal markers;
- bar track converted to symbols or wedges;
- agent-generated prompt-to-figure workflow.

Screenshot workflow:

1. Generate more candidates than needed, aiming for at least 8 screenshot
   candidates.
2. Inspect each candidate manually and with layout metrics where possible.
3. Critique each screenshot for label overlap, clipped text, legend clarity,
   color use, track density, canvas occupancy, and whitespace.
4. Iterate on layout, crop, panel sizing, track width, label density, and legend
   placement until whitespace is minimized without clipping.
5. Select 4-6 final screenshots for documentation.
6. Select 2-3 of those final screenshots for the manuscript.

Screenshot acceptance criteria:

- tree and legend occupy most of the exported image; avoid large empty margins;
- no important label is clipped;
- no obvious label collisions in the final figure area;
- color choices match the palette role;
- legends explain symbols, wedges, intervals, and palettes;
- screenshots are reproducible from checked-in sessions, configs, or commands;
- image paths and captions are documented.

### 7. Documentation And Manuscript

Private implementation repo:

- add a user-facing color palettes and styling documentation page;
- add prompt-to-figure examples;
- add screenshot gallery with 4-6 final images;
- link the new documentation directly from `README.md`;
- update `docs/API.md`, `docs/CLI.md`, `docs/PYTHON.md`, `docs/R.md`, and
  `.agents/skills/treeviz-agent/` when command or schema surfaces change.

Public docs repo at `../treeviz`:

- mirror the finalized documentation and screenshots after implementation;
- update `README.md`;
- update `mkdocs.yml` navigation;
- keep public examples aligned with the shipped Python package and hosted app.

Manuscript:

- add 2-3 final screenshots to the TreeViz manuscript package;
- write captions that describe TreeViz behavior directly;
- avoid external comparison framing in screenshot captions;
- verify that manuscript image paths render from the manuscript directory.

## Success Criteria

Implementation is complete only when all items below are true.

- Palette registry exists with sequential, diverging, categorical, and neutral
  roles, and at least 10 curated palettes total.
- Palette ids work consistently in the web app, session documents, command API,
  CLI/TOML configs, Python examples, R examples, and agent skill docs.
- Color edit controls are compact across node, clade, label, branch, and track
  styling surfaces, and every control allows direct hex paste.
- Conditional styling rules can map metadata to at least branch color, branch
  width, node color, node size, label color, symbol, and wedge outputs.
- Bar-to-symbol or bar-to-wedge examples support user-defined intervals and
  generate a clear legend.
- At least 4 example sessions are checked in with source data or reproducible
  configs.
- At least 8 screenshot candidates are generated and reviewed.
- The final documentation includes 4-6 selected screenshots with captions and
  reproducibility notes.
- The manuscript includes 2-3 selected screenshots with verified paths.
- Documentation includes 3-4 natural-language prompts and the corresponding
  TreeViz commands, configs, or wrapper code.
- `README.md` links directly to the new documentation.
- Public docs in `../treeviz` are updated after the implementation is verified.
- Relevant checks pass before the work is marked done:
  - focused unit tests for palette and conditional rule resolution;
  - schema generation if session or command schemas change;
  - `bun run check`;
  - `bun run test`;
  - `bun run build`;
  - `bun run check:docs`;
  - `bun run check:skill`;
  - visual screenshot QA using the browser API or Playwright.

## Out Of Scope For This Goal

- Adding a built-in LLM to TreeViz.
- Adding a large runtime dependency solely for palettes.
- Rewriting the rendering engine.
- Adding broad statistical analysis workflows.
- Making feature claims around another tool or manuscript.
- Replacing manual styling entirely; manual edits should remain available.

## Proposed Implementation Order

1. Define palette registry, types, docs, and minimal UI selector.
2. Replace large color editors with the compact swatch plus hex field pattern.
3. Add conditional style rule model and resolver tests.
4. Wire rule outputs into branch, node, label, symbol, wedge, and track
   rendering paths.
5. Add command, TOML, Python, R, and skill documentation.
6. Build example sessions and prompt-to-figure examples.
7. Generate screenshot candidates, critique them, tune layouts, and select final
   images.
8. Add documentation screenshots and manuscript screenshots.
9. Mirror finalized docs and images into `../treeviz`.
10. Run full verification and record final results.

