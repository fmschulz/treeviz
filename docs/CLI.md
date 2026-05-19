# CLI reference

```bash
bun run treeviz <command> [args]
```

Four subcommands. All are typed and emit structured diagnostics.

## `validate <config.toml>`

Type-check a `treeviz.toml` config without producing output.

```bash
bun run treeviz validate examples/diff-expr/treeviz.toml
```

Exits non-zero on validation failure with line/column context.

## `compile <input> -o <output.treeviz.json>`

Compile a TOML config (which references its tree + metadata files) into a single `.treeviz.json` session document. The output is deterministic, version-stamped, and self-contained.

```bash
bun run treeviz compile examples/diff-expr/treeviz.toml -o /tmp/session.treeviz.json
```

Accepts either a TOML config path or a pre-existing `.treeviz.json` (passthrough mode).

## `serve [config|session] [--port <n>]`

Build the SPA + start a local HTTP server with the session pre-loaded. The browser opens directly into the visualization — no file picker needed.

```bash
bun run treeviz serve examples/diff-expr/treeviz.toml --port 5174
```

Useful for local dogfooding and screenshot pipelines.

## `render [config|session] -o <output> [options]`

Headless render via Playwright. Outputs vector SVG, raster PNG, or page PDF without opening a visible browser window.

```bash
bun run treeviz render examples/diff-expr/treeviz.toml \
  -o tree.svg \
  --width 1600 --height 900

bun run treeviz render session.treeviz.json \
  -o tree.png --format png

bun run treeviz render session.treeviz.json \
  -o tree.pdf --format pdf \
  --auto-crop --crop-padding 24 \
  --metrics tree.metrics.json
```

Options:

| Flag                  | Default                | Meaning                                         |
| --------------------- | ---------------------- | ----------------------------------------------- |
| `-o, --output <path>` | _required_             | Output file (`.svg`, `.png`, `.pdf`)            |
| `--format <fmt>`      | `svg`                  | `svg`, `png`, or `pdf`                          |
| `--width <px>`        | 1600                   | Viewport width                                  |
| `--height <px>`       | 1200                   | Viewport height                                 |
| `--port <n>`          | 4174                   | Internal preview-server port                    |
| `--auto-crop`         | off                    | Tighten the exported artifact to visible content |
| `--crop-padding <px>` | 24                     | Padding around auto-cropped content             |
| `--metrics <path>`    | off                    | Write crop/whitespace metrics as JSON           |

`--metrics` records the measured content box, crop box, whitespace margins,
fill ratios, and warnings such as `excess-vertical-whitespace`. Use it in
render checks that need to verify viewport fit.

## Precompiled app package

Build the SPA and package the static app archive:

```bash
bun run build
bun run package:app
```

Launch the bundled app over localhost:

```bash
bun .agents/skills/treeviz-agent/scripts/launch-treeviz-app.ts --port 5174
```

Launch directly into a saved session:

```bash
bun .agents/skills/treeviz-agent/scripts/launch-treeviz-app.ts \
  --session session.treeviz.json \
  --port 5174
```

## TOML config

The CLI reads a `treeviz.toml` that references its inputs and configures the visualization. Minimal example:

```toml
[meta]
name = "Mock Differential Expression"

[tree]
file = "tree.nwk"

[metadata]
file = "metadata.tsv"
key_column = "gene"

[[tracks]]
kind = "color-strip"
column = "module"
category_colors = { query_metabat = "#d7191c" }

[[tracks]]
kind = "heatmap"
columns = ["cond_*"]
palette = "diverging-rdbu"
center = 0
```

Bootstrap/support labels and internal node support markers can be configured
from `[view]`. `show_support` displays numeric internal-node support labels.
The root support value is not drawn because the root has no incoming branch to
label. Split-circle markers are separate from support labels. Category
thresholds are evaluated in order; values that match no category are not drawn.

```toml
[view]
show_support = true
internal_node_marker_attribute = "support"
internal_node_marker_categories = [
  { label = "Low support (<65)", max = 65, max_inclusive = false, color = "#ffffff", stroke = "#111827", size = 9 },
  { label = "Medium support (65-90)", min = 65, max = 90, max_inclusive = true, color = "#9ca3af", size = 9 }
]
```

Clade annotation labels can be configured from `[[branch_rule]]` entries.
Branch styling fields (`color`, `line_width`) apply to the matched clade
subtree. Annotation fields apply to the selected clade root, so one
`clade = "Name"` rule does not duplicate labels on descendant internal nodes.
`label` is already the selector field; use `clade_label` for the displayed
annotation text.

```toml
[[branch_rule]]
clade = "Proteobacteria"
color = "#2563eb"
line_width = 3
clade_label = "Proteobacteria"
clade_label_color = "#1d4ed8"
clade_label_bold = true
clade_label_font_size = 15
clade_background = "rgba(37, 99, 235, 0.12)"
```

These labels render for expanded internal clades in rectangular, circular, and
radial layouts; if the clade is collapsed, the same `clade_label` text is used
for the collapsed wedge label. The same fields are available interactively
through `tree.style-clade` as `patch.label`, `cladeLabelColor`,
`cladeLabelBold`, `cladeLabelFontSize`, and `cladeBackground`.
`clade_background` fills the clade region from the selected ancestor to its
terminal descendants; `clade_label_background` remains accepted as a legacy
alias for older configs. Clade labels reserve white backing before metadata
tracks: a measured column in rectangular layout and a measured radial lane in
circular/radial layouts. The reserved space is measured from the label text and
`clade_label_font_size`, so tracks move outward when clade labels get larger and
move back when they get smaller.

For `color-strip` tracks, `category_colors` is an optional exact value-to-hex
map. Listed categories use those colors in saved `.treeviz.json` sessions and
exports; unlisted categories still use the track palette.

For `bar` tracks, `show_axis` controls the x-axis baseline, tick marks, and
tick labels. `axis_position` may be `"top"` or `"bottom"`. Tick-aligned helper
lines are controlled separately:

```toml
[[track]]
kind = "bar"
column = "abundance"
domain = [0, 1]
show_axis = true
axis_position = "top"
show_helper_lines = true
helper_line_style = "dashed" # or "solid"
helper_line_color = "#cbd5e1"
helper_line_width = 0.75
```

Use `treeviz validate` to check TOML configs before compiling them. The
generated public schema currently describes saved `.treeviz.json` sessions at
`/schema/session-v1.json`; there is no shipped JSON Schema file for
`treeviz.toml` configs.
