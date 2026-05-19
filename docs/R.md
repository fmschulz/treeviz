# Use TreeViz From R

The R wrapper in `packages/r` builds TreeViz-native `.treeviz.json` sessions
from R objects and can open or render them through the existing TreeViz app/CLI.
It does not include a renderer and does not depend on heattree.

Run all R checks through Pixi:

```bash
pixi run -e r r-test
pixi run -e r r-check
```

## Build And Save A Session

```r
source("packages/r/R/treeviz.R")

metadata <- data.frame(
  id = c("A", "B", "C", "D"),
  group = c("alpha", "alpha", "beta", "beta"),
  value = c(1.2, 0.8, 2.1, 1.6),
  stringsAsFactors = FALSE
)

session <- build_session(
  "(A,B,(C,D));",
  metadata = metadata,
  tracks = list(
    list(kind = "color_strip", column_key = "group", title = "Group"),
    list(kind = "gradient", column_key = "value", title = "Value")
  ),
  name = "r-example"
)

validate_session(session)
save_session(session, "r-example.treeviz.json")
```

Supported inputs:

- Newick string.
- Newick/Nexus file path.
- `ape::phylo`.
- `data.frame` and tibble metadata.
- CSV/TSV metadata file path.

## Programmatic Open And Render

```r
view <- view_tree("(A,B);", metadata = data.frame(id = c("A", "B")), browse = FALSE)
view$url
```

`render_tree()` writes a temporary `.treeviz.json` session and calls the TreeViz
CLI render path:

```r
render_tree("(A,B);", metadata = data.frame(id = c("A", "B")), format = "svg")
```

## Multi-Tree Input

```r
sessions <- build_session(list("(A,B);", "(C,D);"))
```

Each output item is an independent `.treeviz.json` session.
