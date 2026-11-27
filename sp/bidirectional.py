
"""Bidirectional Dijkstra's algorithm using two binary heaps.

The forward search follows outgoing edges.
The backward search follows incoming edges using a reverse adjacency list.
"""

from __future__ import annotations

import heapq

from .dijkstra import INF, SearchResult


def build_reverse_adjacency(graph):
    """Build reverse adjacency for a directed graph.

    reverse_adj[v] contains (u, weight) for every original edge u -> v.

    Build this once per graph and reuse it across queries when benchmarking.
    """
    reverse_adj = [[] for _ in range(graph.n)]

    for u, neighbors in enumerate(graph.adj):
        for v, weight in neighbors:
            reverse_adj[v].append((u, weight))

    return reverse_adj


def bidirectional_dijkstra(
    graph,
    source: int,
    target: int,
    return_path: bool = False,
    reverse_adj=None,
) -> SearchResult:
    """Find an exact shortest path using bidirectional Dijkstra.

    Parameters
    ----------
    graph:
        Graph with non-negative edge weights.
    source:
        Starting node.
    target:
        Destination node.
    return_path:
        If True, reconstruct and return the shortest path.
    reverse_adj:
        Optional precomputed reverse adjacency list. If omitted,
        it is constructed for this query.

    Returns
    -------
    SearchResult
        Distance, optional path, settled-node count, and heap counters.
    """

    if source == target:
        return SearchResult(
            distance=0.0,
            path=[source] if return_path else None,
            settled=1,
            heap_pushes=1,
            heap_pops=1,
        )

    # Build reverse adjacency for the backward search.
    if reverse_adj is None:
        reverse_adj = build_reverse_adjacency(graph)

    # Forward search: source -> target.
    dist_f = {source: 0.0}
    heap_f = [(0.0, source)]

    # Backward search: target -> source in the reversed graph.
    dist_b = {target: 0.0}
    heap_b = [(0.0, target)]

    # Parent pointers are only needed when a path is requested.
    parent_f = {source: -1} if return_path else None
    parent_b = {target: -1} if return_path else None

    best_distance = INF
    meeting_node = None

    settled = 0
    heap_pushes = 2
    heap_pops = 0

    def clean_heap(heap, distances):
        """Remove outdated entries and return the smallest valid key."""
        nonlocal heap_pops

        while heap and heap[0][0] != distances.get(heap[0][1], INF):
            heapq.heappop(heap)
            heap_pops += 1

        if not heap:
            return INF

        return heap[0][0]

    def update_best(node, distance_f, distance_b):
        """Update the best complete path found so far."""
        nonlocal best_distance, meeting_node

        candidate = distance_f + distance_b

        if candidate < best_distance:
            best_distance = candidate
            meeting_node = node

    while heap_f and heap_b:

        min_f = clean_heap(heap_f, dist_f)
        min_b = clean_heap(heap_b, dist_b)

        # One search has no more reachable nodes.
        if min_f == INF or min_b == INF:
            break

        # No shorter complete path can be found.
        if best_distance <= min_f + min_b:
            break

        # Expand the search with the smaller minimum distance.
        if min_f <= min_b:

            d, u = heapq.heappop(heap_f)
            heap_pops += 1
            settled += 1

            if u in dist_b:
                update_best(u, d, dist_b[u])

            # Forward expansion follows original outgoing edges.
            for v, weight in graph.adj[u]:
                new_distance = d + weight

                if new_distance < dist_f.get(v, INF):
                    dist_f[v] = new_distance

                    if parent_f is not None:
                        parent_f[v] = u

                    heapq.heappush(heap_f, (new_distance, v))
                    heap_pushes += 1

                    if v in dist_b:
                        update_best(v, new_distance, dist_b[v])

        else:

            d, u = heapq.heappop(heap_b)
            heap_pops += 1
            settled += 1

            if u in dist_f:
                update_best(u, dist_f[u], d)

            # Backward expansion follows incoming original edges.
            for v, weight in reverse_adj[u]:
                new_distance = d + weight

                if new_distance < dist_b.get(v, INF):
                    dist_b[v] = new_distance

                    if parent_b is not None:
                        parent_b[v] = u

                    heapq.heappush(heap_b, (new_distance, v))
                    heap_pushes += 1

                    if v in dist_f:
                        update_best(v, dist_f[v], new_distance)

    # Reconstruct the path if requested.
    path = None

    if return_path and meeting_node is not None:

        # Source -> meeting node.
        left = []
        node = meeting_node

        while node != -1:
            left.append(node)
            node = parent_f[node]

        left.reverse()

        # Meeting node -> target.
        right = []
        node = parent_b[meeting_node]

        while node != -1:
            right.append(node)
            node = parent_b[node]

        path = left + right

    return SearchResult(
        distance=best_distance,
        path=path,
        settled=settled,
        heap_pushes=heap_pushes,
        heap_pops=heap_pops,
    )
