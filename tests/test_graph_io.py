from src.utils.graph_io import (
    generate_random_graph,
    read_graph,
    write_coloring,
    write_graph,
)


def test_write_then_read_graph_roundtrips(tmp_path):
    path = tmp_path / "g.txt"
    write_graph(path, num_vertices=4, edges=[(0, 1), (1, 2), (2, 3)])

    n, edges = read_graph(path)

    assert n == 4
    assert edges == [(0, 1), (1, 2), (2, 3)]


def test_write_graph_matches_required_format(tmp_path):
    path = tmp_path / "g.txt"
    write_graph(path, num_vertices=3, edges=[(0, 1)])

    lines = path.read_text().splitlines()

    assert lines[0] == "3 1"
    assert lines[1] == "0 1"


def test_write_coloring_matches_required_format(tmp_path):
    path = tmp_path / "solution.txt"
    write_coloring(path, coloring={0: 0, 1: 1, 2: 0})

    lines = path.read_text().splitlines()

    assert lines[0] == "2"  # 2 distinct colors used
    assert set(lines[1:]) == {"0 0", "1 1", "0 2"}


def test_generate_random_graph_is_reproducible_with_seed():
    n1, edges1 = generate_random_graph(20, edge_prob=0.3, seed=7)
    n2, edges2 = generate_random_graph(20, edge_prob=0.3, seed=7)

    assert n1 == n2
    assert edges1 == edges2
