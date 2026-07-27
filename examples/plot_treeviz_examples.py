#!/usr/bin/env python3
"""Build public TreeViz examples from the Python package.

Run after installing the package:

    python examples/plot_treeviz_examples.py --out treeviz-example-output

The script writes two metadata-rich sessions, two matching bare sessions, and a
summary JSON file. Static SVG/PNG/PDF export is optional and requires an
compatible external renderer command.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from treeviz import (
    binding_diagnostics,
    build_session,
    leaf_names,
    load_session,
    render_tree,
    save_session,
    session_url,
    tree_stats,
    validate_session,
    view_session,
)


CLADES = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
REGIONS = ["North", "South", "East", "West"]
HOSTS = ["soil", "water", "sediment", "host"]


def make_balanced_newick(labels: list[str], offset: int = 0) -> str:
    """Return deterministic Newick with numeric internal support labels."""

    if len(labels) == 1:
        length = 0.035 + ((offset * 7) % 11) * 0.006
        return f"{labels[0]}:{length:.3f}"

    split = len(labels) // 2
    left = make_balanced_newick(labels[:split], offset + 1)
    right = make_balanced_newick(labels[split:], offset + split + 1)
    support = 58 + ((offset * 13 + len(labels) * 5) % 42)
    length = 0.025 + ((offset * 5 + len(labels)) % 9) * 0.007
    return f"({left},{right}){support}:{length:.3f}"


def make_metadata(labels: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    block = max(1, len(labels) // len(CLADES))
    for index, label in enumerate(labels):
        clade = CLADES[min(index // block, len(CLADES) - 1)]
        rows.append(
            {
                "leaf_id": label,
                "clade": clade,
                "region": REGIONS[index % len(REGIONS)],
                "habitat": HOSTS[(index * 2 + 1) % len(HOSTS)],
                "collection_day": 1 + index * 3,
                "abundance": round(0.25 + ((index * 17) % 91) / 20, 3),
                "score_a": round(((index * 19) % 100) / 100, 3),
                "score_b": round(((index * 23 + 11) % 100) / 100, 3),
                "gc": round(0.32 + ((index * 7) % 31) / 100, 3),
                "marker_present": index % 4 in {0, 1},
                "status": "reference" if index % 10 == 0 else "candidate",
            }
        )
    return rows


def make_tracks(include_text: bool) -> list[dict[str, Any]]:
    tracks: list[dict[str, Any]] = [
        {"kind": "color_strip", "column_key": "clade", "title": "Clade", "width": 16},
        {"kind": "color_strip", "column_key": "region", "title": "Region", "width": 14},
        {"kind": "gradient", "column_key": "abundance", "title": "Abundance", "width": 48},
        {"kind": "heatmap", "column_keys": ["score_a", "score_b"], "title": "Scores", "cell_width": 14},
        {"kind": "bar", "column_key": "collection_day", "title": "Day", "width": 52, "show_axis": True},
        {
            "kind": "binary_dots",
            "column_key": "marker_present",
            "title": "Marker",
            "shape": "circle",
            "color": "#0f766e",
            "width": 16,
        },
    ]
    if include_text:
        tracks.append({"kind": "text", "column_key": "status", "title": "Status", "width": 72})
    return tracks


def make_view(layout: str, leaves: int) -> dict[str, Any]:
    show_labels = leaves <= 30
    return {
        "layout": layout,
        "showSupport": True,
        "showBranchLengths": True,
        "branchScale": 0.72 if layout == "rectangular" else 0.82,
        "leafSpacing": 0.86 if leaves <= 30 else 0.42,
        "metadataScale": 0.9,
        "metadataGap": 0,
        "metadataRowScale": 0.88,
        "showLabels": show_labels,
        "labelFontSize": 11 if show_labels else 9,
        "allowLabelOverlap": False,
        "tipAlignment": "tip",
        "branchColourAttribute": "gc",
        "internalNodeMarkerAttribute": "support",
        "internalNodeMarkerEncoding": "shade",
        "internalNodeMarkerColor": "#0f766e",
        "internalNodeMarkerCategories": [
            {"label": "Low support (<70)", "color": "#d1d5db", "max": 70, "maxInclusive": False, "size": 7},
            {"label": "Medium support (70-90)", "color": "#7dd3fc", "min": 70, "max": 90, "size": 8},
            {"label": "High support (>=90)", "color": "#0f766e", "min": 90, "minInclusive": True, "size": 9},
        ],
        "figureLegendVisible": True,
        "figureLegendSectionIndex": None,
        "stagePanelPositions": {"figureLegend": {"x": 24, "y": 24}},
    }


def example_specs() -> dict[str, dict[str, Any]]:
    lineage_labels = [f"L{i:02d}" for i in range(1, 31)]
    clade_labels = [f"C{i:03d}" for i in range(1, 101)]
    return {
        "lineage_30": {
            "tree": make_balanced_newick(lineage_labels) + ";",
            "metadata": make_metadata(lineage_labels),
            "tracks": make_tracks(include_text=True),
            "view": make_view("rectangular", len(lineage_labels)),
        },
        "clade_100": {
            "tree": make_balanced_newick(clade_labels) + ";",
            "metadata": make_metadata(clade_labels),
            "tracks": make_tracks(include_text=False),
            "view": make_view("circular", len(clade_labels)),
        },
    }


def write_session(
    name: str,
    tree: str,
    metadata: list[dict[str, Any]] | None,
    tracks: list[dict[str, Any]],
    view: dict[str, Any],
    out_dir: Path,
) -> dict[str, Any]:
    session = build_session(
        tree,
        metadata=metadata,
        tracks=tracks if metadata else [],
        view=view,
        name=name,
        row_key_column="leaf_id" if metadata else None,
    )
    validate_session(session)
    session_path = save_session(session, out_dir / f"{name}.treeviz.json")
    loaded = load_session(session_path)
    diagnostics = binding_diagnostics(loaded)
    if metadata and (diagnostics.get("unmatchedLeaves") or diagnostics.get("unmatchedRows")):
        raise RuntimeError(f"{name} metadata did not bind cleanly: {diagnostics}")

    view_obj = view_session(loaded, open_browser=False)
    diagnostic_summary = {
        "unmatched_leaf_count": len(diagnostics.get("unmatchedLeaves") or []),
        "unmatched_row_count": len(diagnostics.get("unmatchedRows") or []),
        "duplicate_count": len(diagnostics.get("duplicates") or []),
    }
    return {
        "session": str(session_path),
        "url": session_url(loaded),
        "notebook_fragment_available": view_obj.fragment is not None,
        "leaf_count": len(leaf_names(loaded)),
        "tree_stats": tree_stats(loaded),
        "binding_diagnostics": diagnostic_summary,
    }


def render_outputs(
    name: str,
    spec: dict[str, Any],
    out_dir: Path,
    formats: list[str],
    renderer_command: list[str],
) -> dict[str, str]:
    outputs: dict[str, str] = {}
    for fmt in formats:
        path = out_dir / f"{name}.{fmt}"
        metrics_path = out_dir / f"{name}.{fmt}.metrics.json"
        render_tree(
            spec["tree"],
            metadata=spec.get("metadata"),
            tracks=spec.get("tracks") or [],
            view=spec["view"],
            format=fmt,
            output=path,
            command=renderer_command,
            width=1500,
            height=900 if spec["view"]["layout"] == "circular" else 760,
            auto_crop=True,
            crop_padding=24,
            metrics=metrics_path,
        )
        outputs[fmt] = str(path)
        outputs[f"{fmt}_metrics"] = str(metrics_path)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Build public TreeViz Python example sessions.")
    parser.add_argument("--out", type=Path, default=Path("treeviz-example-output"), help="Output directory.")
    parser.add_argument("--render", action="store_true", help="Render static SVG/PNG/PDF files.")
    parser.add_argument(
        "--formats",
        nargs="+",
        default=["svg", "png", "pdf"],
        choices=["svg", "png", "pdf"],
        help="Static formats to render when --render is set.",
    )
    parser.add_argument(
        "--renderer-command",
        nargs="+",
        default=None,
        help=(
            "Compatible renderer command, for example: "
            "--renderer-command /path/to/treeviz-renderer"
        ),
    )
    parser.add_argument(
        "--skip-static",
        action="store_true",
        help="Deprecated alias for the default behavior; static rendering is off unless --render is set.",
    )
    args = parser.parse_args()

    if args.render and not args.renderer_command:
        parser.error(
            "--render requires --renderer-command, for example: "
            "--renderer-command /path/to/treeviz-renderer"
        )

    args.out.mkdir(parents=True, exist_ok=True)
    specs = example_specs()
    report: dict[str, Any] = {}

    for name, spec in specs.items():
        report[name] = write_session(
            name,
            spec["tree"],
            spec["metadata"],
            spec["tracks"],
            spec["view"],
            args.out,
        )
        bare_name = f"{name}_bare"
        report[bare_name] = write_session(
            bare_name,
            spec["tree"],
            None,
            [],
            {**spec["view"], "showMetadata": False, "figureLegendVisible": False},
            args.out,
        )

        if args.render and not args.skip_static:
            report[name]["static_outputs"] = render_outputs(
                name,
                spec,
                args.out,
                args.formats,
                args.renderer_command,
            )

    report_path = args.out / "summary.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output_dir": str(args.out), "summary": str(report_path)}, indent=2))


if __name__ == "__main__":
    main()
