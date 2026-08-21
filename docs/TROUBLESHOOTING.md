# Troubleshooting

## Metadata Rows Do Not Match Leaves

Check the row-key column first. Its values should match the visible tree leaf
labels exactly unless you intentionally use normalization.

Common causes:

- the wrong row-key column was selected;
- metadata uses different case or underscores than the tree labels;
- tree labels contain prefixes, suffixes, or quoted-label decorations;
- metadata has rows for leaves that are not in the tree;
- the tree has leaves that are missing from metadata.

In Python, inspect:

```python
from treeviz import binding_diagnostics

binding_diagnostics(session)
```

In the browser API, inspect diagnostics after metadata import:

```js
window.__treeviz.getDiagnostics()
```

## The Inline Notebook View Is Missing

Sessions up to 256 KB of encoded URL fragment (roughly 1,500 tips with a few
tracks) are embedded inline. Larger sessions are too large for inline display
and should be saved as `.treeviz.json` instead. The hosted app allows framing
(`frame-ancestors *`); a blank iframe on a self-hosted copy usually means a
`X-Frame-Options` or `frame-ancestors` header on that server.

```python
view = view_session(session, open_browser=False)
view.fragment
```

If `fragment` is `None`, save the session and open it in the browser.

## A Figure Has Too Much Whitespace

Tune the layout before enlarging the canvas:

- reduce branch scale;
- reduce leaf spacing if labels still read clearly;
- reduce metadata gap;
- reduce label size when labels collide;
- enable auto-crop for static exports.

For automated checks, write crop metrics during rendering and inspect the
reported whitespace margins.

## Labels Or Tracks Are Clipped

Increase canvas size only after checking layout settings. Labels, clade
annotations, metadata tracks, and legends all need space. Re-render after the
final layout change and inspect the latest figure.

## Browser API Is Not Available

Open TreeViz with `?api=1`:

```text
https://treeviz.newlineages.com/?api=1
```

Then wait for `window.__treeviz` before issuing commands.
