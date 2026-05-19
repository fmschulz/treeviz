#!/usr/bin/env python3
"""Reroot a Newick tree using a metadata-defined leaf set.

This helper is intentionally dependency-free. It is designed for TreeViz agent
workflows where a user names a taxon in a TSV/CSV metadata file and wants a
repeatable reroot, with ambiguous rows excluded.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path
from typing import Iterable


class Node:
    __slots__ = ("name", "length", "children", "parent", "id")

    def __init__(self) -> None:
        self.name = ""
        self.length: float | None = None
        self.children: list[Node] = []
        self.parent: Node | None = None
        self.id = -1


def parse_newick(text: str) -> Node:
    text = text.strip()
    if text.endswith(";"):
        text = text[:-1]
    index = 0
    next_id = 0

    def parse_name() -> str:
        nonlocal index
        if index < len(text) and text[index] == "'":
            index += 1
            parts: list[str] = []
            while index < len(text):
                char = text[index]
                if char == "'":
                    if index + 1 < len(text) and text[index + 1] == "'":
                        parts.append("'")
                        index += 2
                        continue
                    index += 1
                    break
                parts.append(char)
                index += 1
            return "".join(parts)
        start = index
        while index < len(text) and text[index] not in ":,()":
            index += 1
        return text[start:index].strip()

    def parse_subtree() -> Node:
        nonlocal index, next_id
        node = Node()
        node.id = next_id
        next_id += 1

        if index < len(text) and text[index] == "(":
            index += 1
            while True:
                child = parse_subtree()
                child.parent = node
                node.children.append(child)
                if index >= len(text):
                    raise ValueError("unexpected end of Newick inside child list")
                if text[index] == ",":
                    index += 1
                    continue
                if text[index] == ")":
                    index += 1
                    break
                raise ValueError(f"unexpected token at {index}: {text[index:index + 30]!r}")

        node.name = parse_name()
        if index < len(text) and text[index] == ":":
            index += 1
            start = index
            while index < len(text) and text[index] not in ",()":
                index += 1
            raw = text[start:index].strip()
            node.length = float(raw) if raw else None
        return node

    root = parse_subtree()
    if index != len(text):
        raise ValueError(f"trailing Newick content at {index}: {text[index:index + 30]!r}")
    return root


def walk_preorder(node: Node) -> Iterable[Node]:
    yield node
    for child in node.children:
        yield from walk_preorder(child)


def walk_postorder(node: Node) -> Iterable[Node]:
    for child in node.children:
        yield from walk_postorder(child)
    yield node


def rooted_leaves(node: Node) -> list[Node]:
    if not node.children:
        return [node]
    out: list[Node] = []
    for child in node.children:
        out.extend(rooted_leaves(child))
    return out


def undirected_leaves(node: Node, parent: Node | None = None) -> list[Node]:
    neighbors: list[Node] = []
    if node.parent is not None:
        neighbors.append(node.parent)
    neighbors.extend(node.children)
    children = [candidate for candidate in neighbors if candidate is not parent]
    if not children:
        return [node]
    out: list[Node] = []
    for child in children:
        out.extend(undirected_leaves(child, node))
    return out


def edge_length(a: Node, b: Node) -> float | None:
    if b.parent is a:
        return b.length
    if a.parent is b:
        return a.length
    raise ValueError("nodes are not adjacent")


def quote_name(name: str) -> str:
    if not name:
        return ""
    if re.search(r"[\s,:;()']", name):
        return "'" + name.replace("'", "''") + "'"
    return name


def format_length(value: float | None) -> str:
    if value is None:
        return ""
    return ":" + format(float(value), ".10g")


def serialize_rerooted(root: Node, row_by_leaf: dict[str, dict[str, str]], prefer_category: str | None, category_column: str | None) -> str:
    def order_root_neighbors(node: Node, parent: Node | None, children: list[Node]) -> list[Node]:
        if parent is not None or not prefer_category or not category_column:
            return children

        def score(child: Node) -> tuple[int, int]:
            names = [leaf.name for leaf in undirected_leaves(child, node)]
            counts = Counter(row_by_leaf.get(name, {}).get(category_column, "") for name in names)
            return (-counts[prefer_category], len(names))

        return sorted(children, key=score)

    def rec(node: Node, parent: Node | None) -> str:
        neighbors: list[Node] = []
        if node.parent is not None:
            neighbors.append(node.parent)
        neighbors.extend(node.children)
        children = [candidate for candidate in neighbors if candidate is not parent]
        children = order_root_neighbors(node, parent, children)
        if children:
            text = "(" + ",".join(rec(child, node) for child in children) + ")" + quote_name(node.name)
        else:
            text = quote_name(node.name)
        if parent is not None:
            text += format_length(edge_length(node, parent))
        return text

    return rec(root, None) + ";\n"


def read_metadata(path: Path, row_key: str, delimiter: str | None) -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    text = path.read_text()
    if delimiter is None:
        delimiter = "\t" if path.suffix.lower() in {".tsv", ".tab"} else ","
    rows = list(csv.DictReader(text.splitlines(), delimiter=delimiter))
    if not rows:
        raise ValueError(f"metadata file has no rows: {path}")
    if row_key not in rows[0]:
        raise ValueError(f"row key column {row_key!r} not found; columns: {', '.join(rows[0].keys())}")
    return rows, {row[row_key]: row for row in rows if row.get(row_key)}


def select_metadata_leaves(rows: list[dict[str, str]], args: argparse.Namespace) -> set[str]:
    exclude = re.compile(args.exclude_regex, re.I) if args.exclude_regex else None
    selected: set[str] = set()
    for row in rows:
        if row.get(args.match_column) != args.match_value:
            continue
        blob = " ".join(str(value) for value in row.values())
        if exclude and exclude.search(blob):
            continue
        leaf = row.get(args.row_key)
        if leaf:
            selected.add(leaf)
    return selected


def build_descendant_index(root: Node, selected: set[str]) -> dict[int, tuple[set[str], set[str]]]:
    index: dict[int, tuple[set[str], set[str]]] = {}
    for node in walk_postorder(root):
        if not node.children:
            names = {node.name}
        else:
            names = set().union(*(index[child.id][0] for child in node.children))
        index[node.id] = (names, names & selected)
    return index


def smallest_mrca(root: Node, index: dict[int, tuple[set[str], set[str]]], selected: set[str]) -> Node:
    candidates = [node for node in walk_preorder(root) if selected <= index[node.id][0]]
    if not candidates:
        raise ValueError("selected leaves are not present in the tree")
    return min(candidates, key=lambda node: len(index[node.id][0]))


def choose_target(root: Node, index: dict[int, tuple[set[str], set[str]]], selected: set[str], args: argparse.Namespace) -> tuple[Node, str]:
    total = len(index[root.id][0])
    full = smallest_mrca(root, index, selected)
    full_size = len(index[full.id][0])
    if full_size <= total * args.max_clade_fraction:
        return full, "full-mrca"

    candidates: list[tuple[int, float, int, Node]] = []
    for node in walk_preorder(root):
        names, selected_here = index[node.id]
        if len(names) < 2 or len(names) > total * args.max_clade_fraction:
            continue
        if len(selected_here) < args.min_target_leaves:
            continue
        purity = len(selected_here) / len(names)
        if purity >= args.min_purity:
            candidates.append((len(selected_here), purity, -len(names), node))
    if not candidates:
        return full, "broad-full-mrca-no-concentrated-clade"
    return max(candidates, key=lambda item: (item[0], item[1], item[2]))[3], "largest-concentrated-clade"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree", required=True, type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--row-key", default="leaf")
    parser.add_argument("--match-column", required=True)
    parser.add_argument("--match-value", required=True)
    parser.add_argument("--exclude-regex", default="")
    parser.add_argument("--category-column", default="")
    parser.add_argument("--prefer-category", default="")
    parser.add_argument("--delimiter", choices=["tab", "comma"], default=None)
    parser.add_argument("--min-target-leaves", type=int, default=2)
    parser.add_argument("--min-purity", type=float, default=0.75)
    parser.add_argument("--max-clade-fraction", type=float, default=0.5)
    args = parser.parse_args()

    delimiter = {"tab": "\t", "comma": ","}.get(args.delimiter)
    rows, row_by_leaf = read_metadata(args.metadata, args.row_key, delimiter)
    selected = select_metadata_leaves(rows, args)
    if not selected:
        raise SystemExit("no metadata rows matched the requested predicate")

    root = parse_newick(args.tree.read_text())
    tree_leaf_names = {leaf.name for leaf in rooted_leaves(root)}
    selected_in_tree = selected & tree_leaf_names
    missing = selected - tree_leaf_names
    if not selected_in_tree:
        raise SystemExit("none of the selected metadata leaves are present in the tree")

    index = build_descendant_index(root, selected_in_tree)
    target, reason = choose_target(root, index, selected_in_tree, args)
    target_names, target_selected = index[target.id]

    args.output.write_text(
        serialize_rerooted(
            target,
            row_by_leaf,
            args.prefer_category or None,
            args.category_column or None,
        )
    )

    category_counts = Counter(row_by_leaf.get(name, {}).get(args.category_column, "") for name in target_names) if args.category_column else Counter()
    print(f"selected metadata leaves: {len(selected)}")
    print(f"selected leaves in tree: {len(selected_in_tree)}")
    print(f"selected leaves missing from tree: {len(missing)}")
    print(f"reroot reason: {reason}")
    print(f"reroot node id: {target.id}")
    print(f"reroot node label/support: {target.name or '<none>'}")
    print(f"reroot clade leaves: {len(target_names)}")
    print(f"reroot selected leaves: {len(target_selected)}")
    print(f"reroot purity: {len(target_selected) / len(target_names):.3f}")
    if category_counts:
        print("reroot category composition:")
        for value, count in category_counts.most_common():
            print(f"  {value or '<missing>'}: {count}")
    print(f"wrote: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
