"""Minimal graph container shared by every algorithm (same structure = fair timing)."""
from __future__ import annotations

import pickle
from collections import deque
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Graph:
    name: str
    adj: list[list[tuple[int, float]]]          # adj[u] = [(v, weight), ...]
    coords: list[tuple[float, float]] | None = None  # (x, y) per node; None for non-road graphs
    directed: bool = True

    @property
    def n(self) -> int:
        return len(self.adj)

    @property
    def m(self) -> int:
        """Number of stored (directed) arcs."""
        return sum(len(a) for a in self.adj)

    def summary(self) -> str:
        return f"{self.name}: n={self.n:,} nodes, m={self.m:,} arcs, coords={'yes' if self.coords else 'no'}"

    # ---------- persistence ----------
    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load(path: Path) -> "Graph":
        with open(path, "rb") as f:
            return pickle.load(f)

    # ---------- helpers ----------
    def to_networkx(self):
        """Only used for validation (NetworkX is not used by the algorithms themselves)."""
        import networkx as nx

        G = nx.DiGraph()
        G.add_nodes_from(range(self.n))
        for u, nbrs in enumerate(self.adj):
            for v, w in nbrs:
                G.add_edge(u, v, weight=w)
        return G

    def largest_component(self) -> "Graph":
        """Restrict to the largest weakly connected component and relabel nodes 0..k-1."""
        und = [set() for _ in range(self.n)]
        for u, nbrs in enumerate(self.adj):
            for v, _ in nbrs:
                und[u].add(v)
                und[v].add(u)
        seen = [False] * self.n
        best: list[int] = []
        for s in range(self.n):
            if seen[s]:
                continue
            seen[s] = True
            comp, q = [], deque([s])
            while q:
                u = q.popleft()
                comp.append(u)
                for v in und[u]:
                    if not seen[v]:
                        seen[v] = True
                        q.append(v)
            if len(comp) > len(best):
                best = comp
        if len(best) == self.n:
            return self
        new_id = {old: i for i, old in enumerate(sorted(best))}
        adj = [[] for _ in new_id]
        for old, i in new_id.items():
            adj[i] = [(new_id[v], w) for v, w in self.adj[old] if v in new_id]
        coords = [self.coords[old] for old in sorted(best)] if self.coords else None
        return Graph(self.name, adj, coords, self.directed)


def build_graph(name, n, edges, coords=None, directed=True) -> Graph:
    """Build a Graph from (u, v, w) edges; parallel arcs keep the minimum weight, self-loops dropped."""
    best = [dict() for _ in range(n)]
    for u, v, w in edges:
        if u == v:
            continue
        if v not in best[u] or w < best[u][v]:
            best[u][v] = w
        if not directed and (u not in best[v] or w < best[v][u]):
            best[v][u] = w
    adj = [list(d.items()) for d in best]
    return Graph(name, adj, coords, directed)
