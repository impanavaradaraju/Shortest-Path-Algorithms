
import math
import random

import networkx as nx
import pytest

from sp.bidirectional import (
    bidirectional_dijkstra,
    build_reverse_adjacency,
)
from sp.graph import build_graph


def random_graph(n=300, m=1200, seed=0, directed=True):
    rng = random.Random(seed)

    edges = [
        (
            rng.randrange(n),
            rng.randrange(n),
            rng.uniform(1, 50),
        )
        for _ in range(m)
    ]

    return build_graph("random", n, edges, None, directed)


@pytest.mark.parametrize("directed", [True, False])
def test_matches_networkx(directed):
    graph = random_graph(directed=directed)
    reference = graph.to_networkx()

    reverse_adj = build_reverse_adjacency(graph)
    rng = random.Random(1)

    for _ in range(200):
        source = rng.randrange(graph.n)
        target = rng.randrange(graph.n)

        try:
            expected = nx.dijkstra_path_length(
                reference, source, target
            )
        except nx.NetworkXNoPath:
            expected = math.inf

        result = bidirectional_dijkstra(
            graph,
            source,
            target,
            reverse_adj=reverse_adj,
        )

        assert math.isclose(
            result.distance,
            expected,
            rel_tol=1e-9,
        )


def test_path_is_valid():
    graph = random_graph()
    reverse_adj = build_reverse_adjacency(graph)

    result = bidirectional_dijkstra(
        graph,
        0,
        150,
        return_path=True,
        reverse_adj=reverse_adj,
    )

    if result.distance < math.inf:
        assert result.path[0] == 0
        assert result.path[-1] == 150

        total_weight = sum(
            dict(graph.adj[u])[v]
            for u, v in zip(result.path, result.path[1:])
        )

        assert math.isclose(
            total_weight,
            result.distance,
            rel_tol=1e-9,
        )


def test_source_equals_target():
    graph = random_graph()

    result = bidirectional_dijkstra(graph, 5, 5, return_path=True)

    assert result.distance == 0
    assert result.path == [5]


def test_unreachable_target():
    graph = build_graph(
        "disconnected",
        4,
        [(0, 1, 2.0), (2, 3, 3.0)],
        directed=True,
    )

    result = bidirectional_dijkstra(graph, 0, 3)

    assert result.distance == math.inf
    assert result.path is None


def test_parallel_edges():
    graph = build_graph(
        "parallel",
        3,
        [
            (0, 1, 10.0),
            (0, 1, 2.0),
            (1, 2, 3.0),
        ],
    )

    result = bidirectional_dijkstra(graph, 0, 2)

    assert result.distance == 5.0
