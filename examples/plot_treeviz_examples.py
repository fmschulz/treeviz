#!/usr/bin/env python3
"""Build and plot TreeViz examples from the Python package.

Run after installing the package:

    python examples/plot_treeviz_examples.py --out /tmp/treeviz-python-plots

The script can build sessions and hosted TreeViz URLs. Static SVG/PNG/PDF
export requires an installed TreeViz renderer or an implementation checkout
with Bun available. Static outputs are auto-cropped and write crop metrics for
visual QA.
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
    view_tree,
)


EXAMPLES: dict[str, dict[str, Any]] = {
    "variant_surveillance": {
        "tree": (
            "((Alpha_01:0.09,Alpha_02:0.08)Alpha:0.05,"
            "(Beta_01:0.07,(Beta_02:0.04,Beta_03:0.05)Beta_inner:0.03)Beta:0.06,"
            "(Gamma_01:0.10,Gamma_02:0.09)Gamma:0.04);"
        ),
        "metadata": [
            {"sample": "Alpha_01", "lineage": "Alpha", "region": "North", "collection_day": 4, "viral_load": 18.4, "has_marker": True},
            {"sample": "Alpha_02", "lineage": "Alpha", "region": "North", "collection_day": 7, "viral_load": 16.2, "has_marker": True},
            {"sample": "Beta_01", "lineage": "Beta", "region": "West", "collection_day": 11, "viral_load": 12.1, "has_marker": False},
            {"sample": "Beta_02", "lineage": "Beta", "region": "West", "collection_day": 13, "viral_load": 10.8, "has_marker": False},
            {"sample": "Beta_03", "lineage": "Beta", "region": "South", "collection_day": 15, "viral_load": 11.6, "has_marker": True},
            {"sample": "Gamma_01", "lineage": "Gamma", "region": "East", "collection_day": 20, "viral_load": 22.4, "has_marker": True},
            {"sample": "Gamma_02", "lineage": "Gamma", "region": "East", "collection_day": 23, "viral_load": 19.7, "has_marker": False},
        ],
        "row_key_column": "sample",
        "tracks": [
            {"kind": "color_strip", "column_key": "lineage", "title": "Lineage"},
            {"kind": "color_strip", "column_key": "region", "title": "Region"},
            {"kind": "gradient", "column_key": "viral_load", "title": "Viral load"},
            {"kind": "bar", "column_key": "collection_day", "title": "Collection day", "show_axis": True},
            {"kind": "binary_dots", "column_key": "has_marker", "title": "Marker"},
        ],
    },
    "enzyme_families": {
        "tree": (
            "((HydA_1:0.13,HydA_2:0.11)HydA:0.08,"
            "((NiFe_1:0.09,NiFe_2:0.12)NiFe:0.07,"
            "(Ech_1:0.10,Ech_2:0.11)Ech:0.05)Group2:0.06,"
            "Fdh_1:0.17);"
        ),
        "metadata": [
            {"gene": "HydA_1", "family": "FeFe", "habitat": "sediment", "score_a": 0.91, "score_b": 0.64, "note": "reference"},
            {"gene": "HydA_2", "family": "FeFe", "habitat": "sediment", "score_a": 0.86, "score_b": 0.58, "note": "candidate"},
            {"gene": "NiFe_1", "family": "NiFe", "habitat": "hot_spring", "score_a": 0.78, "score_b": 0.82, "note": "candidate"},
            {"gene": "NiFe_2", "family": "NiFe", "habitat": "hot_spring", "score_a": 0.81, "score_b": 0.79, "note": "reference"},
            {"gene": "Ech_1", "family": "Ech", "habitat": "rumen", "score_a": 0.67, "score_b": 0.88, "note": "candidate"},
            {"gene": "Ech_2", "family": "Ech", "habitat": "rumen", "score_a": 0.71, "score_b": 0.84, "note": "candidate"},
            {"gene": "Fdh_1", "family": "Fdh", "habitat": "marine", "score_a": 0.74, "score_b": 0.69, "note": "outgroup"},
        ],
        "row_key_column": "gene",
        "tracks": [
            {"kind": "color_strip", "column_key": "family", "title": "Family"},
            {"kind": "heatmap", "column_keys": ["score_a", "score_b"], "title": "Scores"},
            {"kind": "text", "column_key": "note", "title": "Note"},
        ],
    },
}


def default_renderer_cwd() -> Path | None:
    root = Path(__file__).resolve().parents[3]
    if (root / "package.json").is_file() and (root / "src/cli/cli.ts").is_file():
        return root
    return None


def write_example(
    name: str,
    example: dict[str, Any],
    out_dir: Path,
    formats: list[str],
    renderer_cwd: Path | None,
    skip_static: bool,
) -> dict[str, Any]:
    session = build_session(
        example["tree"],
        metadata=example["metadata"],
        tracks=example["tracks"],
        name=name,
        row_key_column=example["row_key_column"],
    )
    validate_session(session)

    session_path = save_session(session, out_dir / f"{name}.treeviz.json")
    loaded = load_session(session_path)
    diagnostics = binding_diagnostics(loaded)
    if diagnostics.get("unmatchedLeaves") or diagnostics.get("unmatchedRows"):
        raise RuntimeError(f"{name} metadata did not bind cleanly: {diagnostics}")

    view = view_session(loaded, open_browser=False)
    direct_view = view_tree(
        example["tree"],
        metadata=example["metadata"],
        tracks=example["tracks"],
        open_browser=False,
        name=name,
        row_key_column=example["row_key_column"],
    )
    if direct_view.fragment is None:
        raise RuntimeError(f"{name} is too large for URL-fragment notebook display")

    outputs: dict[str, str] = {}
    if not skip_static:
        for fmt in formats:
            path = out_dir / f"{name}.{fmt}"
            metrics_path = out_dir / f"{name}.{fmt}.metrics.json"
            render_tree(
                example["tree"],
                metadata=example["metadata"],
                tracks=example["tracks"],
                format=fmt,
                output=path,
                width=1400,
                height=620,
                auto_crop=True,
                crop_padding=24,
                metrics=metrics_path,
                cwd=renderer_cwd,
            )
            outputs[fmt] = str(path)
            outputs[f"{fmt}_metrics"] = str(metrics_path)

    return {
        "session": str(session_path),
        "url": session_url(loaded),
        "notebook_fragment_available": view.fragment is not None,
        "leaf_names": leaf_names(loaded),
        "tree_stats": tree_stats(loaded),
        "binding_diagnostics": diagnostics,
        "static_outputs": outputs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and plot example TreeViz Python sessions.")
    parser.add_argument("--out", type=Path, default=Path("treeviz-python-plots"), help="Output directory.")
    parser.add_argument(
        "--formats",
        nargs="+",
        default=["svg", "png", "pdf"],
        choices=["svg", "png", "pdf"],
        help="Static formats to render through the TreeViz CLI.",
    )
    parser.add_argument(
        "--renderer-cwd",
        type=Path,
        default=default_renderer_cwd(),
        help="Directory containing the TreeViz browser app and CLI. Defaults to the source checkout root.",
    )
    parser.add_argument(
        "--skip-static",
        action="store_true",
        help="Only write .treeviz.json files and hosted URLs; do not call the external renderer.",
    )
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    report = {
        name: write_example(name, example, args.out, args.formats, args.renderer_cwd, args.skip_static)
        for name, example in EXAMPLES.items()
    }
    report_path = args.out / "summary.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output_dir": str(args.out), "summary": str(report_path)}, indent=2))


if __name__ == "__main__":
    main()
