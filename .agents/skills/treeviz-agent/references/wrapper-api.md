# Python And R Wrappers

Use this reference when an agent needs TreeViz from Python, Jupyter, R, or a
programmatic pipeline. The wrappers are TreeViz-native adapters. They produce
`.treeviz.json` sessions and open or render the existing TreeViz app; they do
not implement a second renderer.

## Rules

- Use Pixi-managed environments for all Python, Jupyter, and R work.
- Do not use system Python or system R.
- Do not depend on, copy, or mimic heattree.
- Use TreeViz-native exported names such as `build_session`, `save_session`,
  `view_tree`, and `render_tree`.
- Validate generated sessions against `treeviz-session.schema.json`.

## Python

After publication, install the Python package as `treeviz-phylo`; import it as
`treeviz`:

```bash
pip install treeviz-phylo
```

Development installs from a source checkout are maintained in the private
implementation repository.

Typical usage:

```python
from treeviz import build_session, save_session, view_tree

metadata = [
    {"id": "A", "group": "alpha", "value": 1.2},
    {"id": "B", "group": "alpha", "value": 0.8},
    {"id": "C", "group": "beta", "value": 2.1},
    {"id": "D", "group": "beta", "value": 1.6},
]
tracks = [
    {"kind": "color_strip", "column_key": "group", "title": "Group"},
    {"kind": "gradient", "column_key": "value", "title": "Value"},
]

session = build_session("(A,B,(C,D));", metadata=metadata, tracks=tracks, name="example")
save_session(session, "example.treeviz.json")
view = view_tree("(A,B,(C,D));", metadata=metadata, tracks=tracks, open_browser=False)
```

Notebook objects expose `_repr_html_()` so Jupyter can display an iframe backed
by the hosted TreeViz app and a share-fragment session when the session is small
enough for a URL fragment.

Notebook examples should explicitly call `display(view)`. When a saved session
and inline view are both shown, pass the same `tracks` and `view` settings to
`build_session(...)` and `view_tree(...)`, then assert the generated track
configuration matches.

Run Python checks through Pixi:

```bash
pixi run -e py py-test
pixi run -e py py-build
pixi run -e py py-twine-check
pixi run -e py py-package-check
pixi run -e py py-notebook
pixi run -e py py-kernel
```

After `py-notebook`, inspect `/tmp/treeviz-python-notebook.ipynb` for an iframe
output and `/tmp/treeviz-notebook-coronavirus.png` for the static render.
For interactive Jupyter on `nb.newlineages.com`, select `Python (Pixi)`; that
hosted kernel uses the nearest parent `pixi.toml`. For local Jupyter servers,
launch Jupyter through Pixi or select the named `TreeViz (pixi py)` kernel. Do
not rely on a generic system `Python 3` kernel.

## R

Typical usage:

```r
library(treeviz)

metadata <- data.frame(
  id = c("A", "B", "C", "D"),
  group = c("alpha", "alpha", "beta", "beta"),
  value = c(1.2, 0.8, 2.1, 1.6)
)

session <- build_session("(A,B,(C,D));", metadata = metadata, name = "example")
save_session(session, "example.treeviz.json")
view_tree("(A,B,(C,D));", metadata = metadata, browse = FALSE)
```

Run R checks through Pixi:

```bash
pixi run -e r Rscript packages/r/tests/smoke.R
```

## Programmatic Browser Check

For any wrapper-generated session, launch the bundled app and inspect the API:

```bash
bun .agents/skills/treeviz-agent/scripts/launch-treeviz-app.ts \
  --session path/to/session.treeviz.json \
  --headless \
  --no-open
```

Open the printed URL with Playwright, wait for `window.__treeviz`, then check:

- `getDiagnostics()` has no errors.
- `getSession()` is non-null.
- `exportSvg()` returns non-empty SVG.
