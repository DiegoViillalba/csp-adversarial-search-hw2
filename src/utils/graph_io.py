"""Graph instance I/O, in the exact format required by the assignment:

Input format:
    line 1:        <num_vertices> <num_edges>
    lines 2..m+1:   <u> <v>           (0-indexed vertex ids, one edge per line)

Output format (graph coloring solution):
    line 1:         <num_colors_used>
    lines 2..n+1:   <color> <vertex>  (one line per vertex)

Nothing here decides *how* to color a graph — it only reads/writes instances
and solutions, and generates random test instances so you have 50/1000-node
graphs to run against.
"""
from __future__ import annotations

import random
from pathlib import Path


def read_graph(path: str | Path) -> tuple[int, list[tuple[int, int]]]:
    """Returns (num_vertices, edges)."""
    path = Path(path)
    with path.open() as f:
        lines = [line.split() for line in f if line.strip()]

    num_vertices, num_edges = int(lines[0][0]), int(lines[0][1])
    edges = [(int(u), int(v)) for u, v in lines[1 : 1 + num_edges]]

    if len(edges) != num_edges:
        raise ValueError(
            f"{path}: header declares {num_edges} edges but {len(edges)} were read"
        )
    return num_vertices, edges


def write_graph(path: str | Path, num_vertices: int, edges: list[tuple[int, int]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(f"{num_vertices} {len(edges)}\n")
        for u, v in edges:
            f.write(f"{u} {v}\n")


def write_coloring(path: str | Path, coloring: dict[int, int]) -> None:
    """coloring: vertex -> color id (any hashable/int color labels; only the
    count of *distinct* colors actually used is reported on line 1)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    num_colors_used = len(set(coloring.values()))
    with path.open("w") as f:
        f.write(f"{num_colors_used}\n")
        for vertex, color in coloring.items():
            f.write(f"{color} {vertex}\n")


def generate_random_graph(
    num_vertices: int, edge_prob: float, seed: int | None = None
) -> tuple[int, list[tuple[int, int]]]:
    """Erdos-Renyi G(n, p) instance generator, used to produce the 50/1000-node
    graph-coloring instances the assignment asks for. Pure stdlib (no networkx
    dependency for something this simple)."""
    rng = random.Random(seed)
    edges = [
        (u, v)
        for u in range(num_vertices)
        for v in range(u + 1, num_vertices)
        if rng.random() < edge_prob
    ]
    return num_vertices, edges
