"""Dijkstra's algorithm (binary heap, lazy deletion) with search-effort counters."""
from __future__ import annotations

import heapq
from dataclasses import dataclass

INF = float("inf")


@dataclass
class SearchResult:
    distance: float             # INF if target unreachable
    path: list[int] | None      # node list source -> target (only if requested)
    settled: int                # nodes whose final distance was fixed
    heap_pushes: int
    heap_pops: int

    @property
    def heap_ops(self) -> int:
        return self.heap_pushes + self.heap_pops


def dijkstra(graph, source: int, target: int, return_path: bool = False) -> SearchResult:
    """Point-to-point Dijkstra; stops as soon as `target` is settled."""
    adj = graph.adj
    dist = {source: 0.0}
    parent = {source: -1} if return_path else None
    heap = [(0.0, source)]
    pushes, pops, settled = 1, 0, 0

    while heap:
        d, u = heapq.heappop(heap)
        pops += 1
        if d > dist[u]:          # stale heap entry (lazy deletion)
            continue
        settled += 1
        if u == target:
            path = None
            if return_path:
                path, x = [], target
                while x != -1:
                    path.append(x)
                    x = parent[x]
                path.reverse()
            return SearchResult(d, path, settled, pushes, pops)
        for v, w in adj[u]:
            nd = d + w
            if nd < dist.get(v, INF):
                dist[v] = nd
                if parent is not None:
                    parent[v] = u
                heapq.heappush(heap, (nd, v))
                pushes += 1

    return SearchResult(INF, None, settled, pushes, pops)


def dijkstra_all(graph, source: int) -> dict[int, float]:
    """Single-source distances to every reachable node (needed later for ALT preprocessing)."""
    adj = graph.adj
    dist = {source: 0.0}
    heap = [(0.0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist.get(v, INF):
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist
