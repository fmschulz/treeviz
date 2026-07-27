# Example Notes

The public examples are designed to run from a normal PyPI install.

## Python Script

```bash
pip install treeviz-phylo
python examples/plot_treeviz_examples.py --out treeviz-example-output
```

The script generates two deterministic trees:

- `lineage_30`: 30 leaves, rectangular layout, metadata tracks, binary leaf symbols, support markers, and numeric branch coloring.
- `clade_100`: 100 leaves, circular layout, metadata tracks, binary leaf symbols, support markers, and numeric branch coloring.

For each tree, the script also writes a `_bare` session without metadata. This
lets you compare the same topology with and without tracks.

## Static Rendering

If the environment already provides a compatible renderer, add `--render`:

```bash
python examples/plot_treeviz_examples.py \
  --out treeviz-example-output \
  --render \
  --renderer-command /path/to/treeviz-renderer
```

Outputs include `.treeviz.json`, optional SVG/PNG/PDF files, optional crop
metrics, and `summary.json`.

If no renderer command is available, open the generated `.treeviz.json` files
in the hosted browser app:

```text
https://treeviz.newlineages.com/
```

## Notebook Pattern

Use the package in a notebook with `view_tree(...)` or `view_session(...)`:

```python
from IPython.display import display
from treeviz import build_session, view_session

session = build_session(tree, metadata=metadata, tracks=tracks, row_key_column="leaf_id")
display(view_session(session, open_browser=False))
```

Large sessions should be saved as `.treeviz.json` and opened in the browser.
