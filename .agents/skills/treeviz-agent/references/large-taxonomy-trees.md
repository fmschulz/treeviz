# Large Taxonomy Tree Workflow

Use this reference for large phylogenetic trees with query/reference tips, taxonomy color strips, rerooting by named taxon, and publication-style no-label exports.

## Fast File-Based Workflow

Prefer this path when the user already has a Newick tree and metadata table:

1. Read the tree config and metadata headers first.
2. Define query tips by a stable rule from the user, such as `_metabat_` in the leaf name.
3. Build a derived metadata column for the visual track instead of overloading raw taxonomy columns.
4. Make every visible track value explicit:
   - query tips: `query_<label>` so they receive a color instead of a missing gap
   - focus reference taxa: their order/family/class value
   - non-focus references: `other_reference`
5. Compile the TreeViz TOML to `.treeviz.json`.
6. Create separate circular and rectangular session JSONs by changing only `view`.
7. Render one session at a time.
8. Run export cleanup and inspect PNGs.

## Taxonomy Color Strips

Categorical color strips assign palette slots in first-seen visible leaf order. If the exact color for a category matters, either:

- reorder/reroot so the first-seen category order matches the palette, or
- create a dedicated palette whose first slots match the rendered first-seen category order.

For uploaded `.treeviz.json` files, use explicit `categoryColors` on
`color-strip` tracks when specific category colors matter. Palette ids remain
useful as fallback colors for categories not listed in `categoryColors`.

For publication-style outputs, open the Legend panel and use "Display in
figure" on the taxonomy legend section, or call `view.set-figure-legend-section`
with that section index after the color-strip track is present. Move it with
`view.set-panel-position` using `panel: "figureLegend"`; SVG, PNG, and PDF
exports include the plain figure legend at that stage position.

When query tips must match query branch color on a hosted TreeViz instance:

- use a dedicated visual column such as `order_or_query`
- set all query rows to one explicit category such as `query_metabat`
- set `tracks[].categoryColors.query_metabat` to the desired red hex
- set the query branch rule to the same hex

For example, set both `tracks[].categoryColors.query_metabat` and the query
branch rule to `#d7191c`. Do not rely on first-seen palette slot order when an
exact category color is required.

Do not leave query rows blank in the order strip when the user wants query wedges colored. Use the same category color as the query branches if requested.

If a named order appears uncolored, check all of these before changing the renderer:

- the metadata value is present and spelled consistently
- the value is not treated as missing by categorical missing-value rules
- the track column is the derived visual column, not the raw taxonomy column
- the palette slot for that value is visually distinct from neighboring categories
- the rendered SVG contains the expected number of `fill="<color>"` occurrences
- the uploaded `.treeviz.json` has `categoryColors` for exact category colors

## Query And Reference Branches

For query/reference emphasis:

- Style query branches with a specific branch rule, for example `_metabat_` → red.
- Do not add a catch-all black branch rule for references. It prevents dark-mode exports from remapping default branches to white.
- If the output is a `.treeviz.json` meant for a hosted TreeViz site, make the
  branch-rule color match the `categoryColors` value for the query metadata
  category.
- For dark SVG/PNG copies, remap default `#333333` branch strokes to `#f4f7fb` and add the dark canvas background.

## Rerooting From Taxonomy

Before rerooting on a named taxon:

1. Select leaves from metadata.
2. Apply requested exclusions such as `incertae_sedis`.
3. Compute the MRCA of all selected leaves.
4. Report if the selected taxon is not monophyletic.
5. If the MRCA is the whole tree or too broad, use the largest concentrated selected clade only when that is scientifically acceptable for the task.

Use the helper script for repeatable rerooting:

```bash
python .agents/skills/treeviz-agent/scripts/reroot-newick-by-metadata.py \
  --tree input.contree \
  --metadata metadata.tsv \
  --output rerooted.contree \
  --match-column taxonomy_class \
  --match-value Pokkesviricetes \
  --exclude-regex 'incertae[_ ]sedis' \
  --category-column reference_order_wedge \
  --prefer-category Asfuvirales
```

The script prints the selected-leaf count, whether the full MRCA is broad, the reroot clade size, purity, and category composition.

## Circular Versus Rectangular

Circular:

- `showBranchLengths=true` avoids artificial tip-alignment spokes to the metadata wedges.
- Rerooting can move the longest branch-length geometry close to a canvas edge. Render a large canvas, inspect the raw content bbox, then crop.
- Remove the scale-bar layer when the final figure should have no scale bar.

Rectangular:

- Use `showBranchLengths=false` for compact cladogram-like overview figures.
- Reduce `branchScale` aggressively before widening the canvas; values near `0.08` can be appropriate for very dense no-label trees.
- Render rectangular after circular, not in parallel, because the CLI render command uses a shared bootstrap session file.

## Final Checks

Use concrete file checks in addition to visual inspection:

- no `data-tv-layer="scale-bar"` in final SVGs when scale bars are unwanted
- no `stroke-dasharray` unless the user asked for dashed styling
- expected query branch and query wedge color counts
- for uploadable JSON, inspect the session `tracks[0].categoryColors` when exact
  category colors are required
- expected focus taxon color counts, for example all `Asfuvirales` cells are present
- dark SVGs have no default `#333333` branch strokes
- PNG content margins are small enough and the figure is not clipped
