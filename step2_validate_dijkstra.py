"""Step 2: validate our Dijkstra against NetworkX on random start-destination pairs.

Usage
  python step2_validate_dijkstra.py --graphs toronto --pairs 100
"""
import argparse
import math
import random
import time

import networkx as nx

from sp import loaders
from sp.dijkstra import dijkstra
from sp.graph import Graph


def validate(g: Graph, pairs: int, seed: int) -> bool:
    rng = random.Random(seed)
    G = g.to_networkx()
    bad, t_ours, t_nx, settled = 0, 0.0, 0.0, 0
    for _ in range(pairs):
        s, t = rng.randrange(g.n), rng.randrange(g.n)
        t0 = time.perf_counter()
        res = dijkstra(g, s, t, return_path=True)
        t_ours += time.perf_counter() - t0
        t0 = time.perf_counter()
        try:
            ref = nx.dijkstra_path_length(G, s, t, weight="weight")
        except nx.NetworkXNoPath:
            ref = math.inf
        t_nx += time.perf_counter() - t0
        settled += res.settled

        ok = math.isclose(res.distance, ref, rel_tol=1e-9, abs_tol=1e-9)
        if ok and res.path:  # the returned path must also sum to the reported distance
            plen = sum(dict(g.adj[a])[b] for a, b in zip(res.path, res.path[1:]))
            ok = math.isclose(plen, ref, rel_tol=1e-9, abs_tol=1e-9)
        if not ok:
            bad += 1
            print(f"  MISMATCH {s}->{t}: ours={res.distance} networkx={ref}")
    status = "PASS" if bad == 0 else "FAIL"
    print(f"[{status}] {g.name}: {pairs - bad}/{pairs} match | avg settled={settled / pairs:,.0f} "
          f"| ours {t_ours / pairs * 1e3:.2f} ms/query, networkx {t_nx / pairs * 1e3:.2f} ms/query")
    return bad == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graphs", nargs="+", required=True, help="names cached by step 1, e.g. toronto")
    ap.add_argument("--pairs", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    ok = all([validate(Graph.load(loaders.PROCESSED / f"{n}.pkl"), args.pairs, args.seed) for n in args.graphs])
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
