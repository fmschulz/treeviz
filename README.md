# TreeViz

This is the public documentation, examples, issue tracker, and AI-agent skill
repository for TreeViz.

TreeViz is a browser-based phylogenetic tree viewer for Newick, Nexus,
metadata tables, and `.treeviz.json` sessions. The live app is available at:

```text
https://treeviz.newlineages.com/
```

The implementation and package release source are maintained separately in a
private repository. This public repository is intended for users, package
documentation, examples, and agent workflows.

## Documentation

- [Browser usage](docs/BROWSER.md)
- [Python package](docs/PYTHON.md)
- [R wrapper](docs/R.md)
- [Metadata rules](docs/METADATA.md)
- [Browser API](docs/API.md)
- [Agent automation](docs/AGENTS.md)
- [CLI usage](docs/CLI.md)

## Python Package

The PyPI distribution is `treeviz-phylo`; the Python import name is `treeviz`.
After a release is uploaded to PyPI:

```bash
pip install treeviz-phylo
```

Minimal example:

```python
from treeviz import build_session, save_session, validate_session, view_session

tree = "(A:0.1,B:0.2,(C:0.3,D:0.4):0.5);"
session = build_session(tree)
validate_session(session)
save_session(session, "example.treeviz.json")
view = view_session(session, open_browser=False)
view.url
```

See [docs/PYTHON.md](docs/PYTHON.md) for metadata, tracks, notebooks, and
static export notes.

## AI Agent Skill

The TreeViz agent skill lives at:

```text
.agents/skills/treeviz-agent/
```

It includes a pinned browser app archive and helper scripts for local,
agent-driven rendering workflows:

```bash
bun .agents/skills/treeviz-agent/scripts/launch-treeviz-app.ts --port 5174
```

For hosted workflows, agents should use:

```text
https://treeviz.newlineages.com/?api=1
https://treeviz.newlineages.com/?mode=headless&api=1
```

## Issues

Use GitHub issues in this repository for documentation, package usage, and
workflow reports.
