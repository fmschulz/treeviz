# Large Taxonomy Trees

Use this reference for large phylogenetic trees with query/reference tips,
taxonomy color strips, rerooting by named taxon, and dense no-label exports.

## File-Based Preparation

1. Read the Newick/Nexus tree and metadata headers first.
2. Define query tips by a stable rule from the user, such as a prefix or suffix
   in the leaf name.
3. Build derived metadata columns for display instead of overloading raw
   taxonomy columns.
4. Make every visible track value explicit:
   - query tips: `query_<label>`;
   - focus reference taxa: the requested order, family, or class value;
   - non-focus references: `other_reference`.
5. Build a `.treeviz.json` session through Python or the browser API.
6. Create separate session files for rectangular and circular layouts when both
   figures are needed.
7. Render or inspect one layout at a time.

## Taxonomy Color Strips

Categorical color strips depend on category values. Keep display categories
clean and explicit.

When query tips must share branch and track colors:

- use a dedicated visual column such as `order_or_query`;
- set all query rows to one explicit category such as `query_metabat`;
- set `categoryColors.query_metabat` on the color-strip track;
- use the same hex color for query branch styling.

Do not leave query rows blank when the user expects query wedges to be colored.
Use an explicit category instead.

If a named taxon appears uncolored, check:

- the metadata value is present and spelled consistently;
- the value is not treated as missing;
- the displayed track uses the derived visual column;
- the palette or explicit colors make the category distinguishable;
- the session contains the expected metadata rows.

## Query And Reference Branches

For query/reference emphasis:

- style query branches with `tree.style-clade` or stable-key-based branch rules
  derived from the loaded session;
- avoid broad catch-all styling that makes reference branches visually heavy;
- keep branch colors consistent with metadata track colors when the user asks
  for a matched legend.

## Rerooting From Taxonomy

Before rerooting on a named taxon:

1. Select leaves from metadata.
2. Apply requested exclusions such as `incertae_sedis`.
3. Compute or resolve the MRCA.
4. Report if the selected taxon is not monophyletic.
5. If the MRCA is the whole tree or too broad, use a smaller concentrated clade
   only when that matches the user's stated goal.

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

The script reports selected-leaf count, whether the full MRCA is broad, reroot
clade size, purity, and category composition.

## Circular Versus Rectangular

Circular:

- useful for dense overview figures;
- works best when labels are hidden or short;
- should be checked for metadata wedge readability and crop margins.

Rectangular:

- usually best for metadata-heavy figures;
- supports compact labels and track comparison;
- should keep `branchScaleMode: "auto"` unless fixed geometry is required;
- often benefits from tight leaf spacing.

## Final Checks

- no unresolved diagnostics;
- `contentOccupancyX` and `contentOccupancyY` use the available canvas without
  clipping labels;
- expected query and focus categories are present;
- metadata tracks are readable;
- legends have concise titles and item labels;
- PNG/SVG/PDF margins are tight but not clipped;
- final `.treeviz.json` opens cleanly in the hosted app.
