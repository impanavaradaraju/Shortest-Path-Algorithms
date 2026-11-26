"""Step 1: acquire every graph once, convert to sp.graph.Graph, cache in data/processed/.

Usage examples
  python step1_load_graphs.py --graphs toronto
  python step1_load_graphs.py --graphs toronto dimacs-ny-d dimacs-ny-t snap random
  python step1_load_graphs.py            # everything (GTA and Florida are large)
"""
import argparse
import time

from sp import loaders
from sp.graph import Graph

CHOICES = ["toronto", "gta", "dimacs-ny-d", "dimacs-ny-t", "dimacs-fla-d", "dimacs-fla-t", "snap", "random"]


def build(name: str) -> Graph:
    if name == "toronto":
        return loaders.load_osmnx("toronto", "Toronto, Ontario, Canada")
    if name == "gta":
        return loaders.load_osmnx("gta", loaders.GTA_PLACES)
    if name.startswith("dimacs"):
        _, region, kind = name.split("-")
        return loaders.load_dimacs(region.upper(), kind)
    if name == "snap":
        return loaders.load_snap()
    if name == "random":  # sized to match the SNAP graph
        snap_path = loaders.PROCESSED / "snap.pkl"
        ref = Graph.load(snap_path) if snap_path.exists() else loaders.load_snap()
        return loaders.make_random_like(ref)
    raise ValueError(name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graphs", nargs="+", choices=CHOICES, default=CHOICES)
    ap.add_argument("--force", action="store_true", help="rebuild even if cached")
    args = ap.parse_args()

    for name in args.graphs:
        out = loaders.PROCESSED / f"{name}.pkl"
        if out.exists() and not args.force:
            print(f"[skip] {name} already cached -> {Graph.load(out).summary()}")
            continue
        print(f"[load] {name}")
        t0 = time.perf_counter()
        g = build(name)
        g.save(out)
        print(f"  {g.summary()}  ({time.perf_counter() - t0:.1f}s) -> {out}")


if __name__ == "__main__":
    main()
