import math
import random

import networkx as nx
import pytest

from sp.dijkstra import dijkstra, dijkstra_all
from sp.graph import build_graph


def random_graph(n=300, m=1200, seed=0, directed=True):
    rng = random.Random(seed)
    edges = [(rng.randrange(n), rng.randrange(n), rng.uniform(1, 50)) for _ in range(m)]
    return build_graph("rand", n, edges, None, directed)


@pytest.mark.parametrize("directed", [True, False])
def test_matches_networkx(directed):
    g = random_graph(directed=directed)
    G = g.to_networkx()
    rng = random.Random(1)
    for _ in range(200):
        s, t = rng.randrange(g.n), rng.randrange(g.n)
        try:
            ref = nx.dijkstra_path_length(G, s, t)
        except nx.NetworkXNoPath:
            ref = math.inf
        assert math.isclose(dijkstra(g, s, t).distance, ref, rel_tol=1e-9)


def test_path_is_valid_and_counters_sane():
    g = random_graph()
    res = dijkstra(g, 0, 150, return_path=True)
    if res.distance < math.inf:
        assert res.path[0] == 0 and res.path[-1] == 150
        assert math.isclose(sum(dict(g.adj[a])[b] for a, b in zip(res.path, res.path[1:])), res.distance)
    assert res.settled <= res.heap_pops <= res.heap_pushes


def test_source_equals_target():
    g = random_graph()
    res = dijkstra(g, 5, 5)
    assert res.distance == 0 and res.settled == 1


def test_dijkstra_all_agrees_with_point_to_point():
    g = random_graph()
    d = dijkstra_all(g, 0)
    for t in range(0, 300, 17):
        assert math.isclose(dijkstra(g, 0, t).distance, d.get(t, math.inf))


def test_parallel_edges_keep_minimum():
    g = build_graph("p", 2, [(0, 1, 5.0), (0, 1, 3.0)])
    assert dijkstra(g, 0, 1).distance == 3.0
