"""Graph acquisition. OSMnx is used only here; everything is converted to sp.graph.Graph."""
from __future__ import annotations

import gzip
import random
import urllib.request
from pathlib import Path

from .graph import Graph, build_graph

RAW = Path("data/raw")
PROCESSED = Path("data/processed")

GTA_PLACES = [
    "Toronto, Ontario, Canada", "Mississauga, Ontario, Canada", "Brampton, Ontario, Canada",
    "Markham, Ontario, Canada", "Vaughan, Ontario, Canada", "Richmond Hill, Ontario, Canada",
    "Oakville, Ontario, Canada", "Pickering, Ontario, Canada", "Ajax, Ontario, Canada",
]
DIMACS_BASE = "http://www.diag.uniroma1.it/challenge9/data/USA-road-{kind}/USA-road-{kind}.{region}.{ext}.gz"
SNAP_URL = "https://snap.stanford.edu/data/soc-Slashdot0811.txt.gz"


def _download(url: str, dest: Path) -> Path:
    if dest.exists():
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  downloading {url}")
    try:
        urllib.request.urlretrieve(url, dest)
    except Exception as e:  # keep the message actionable
        raise RuntimeError(f"Download failed ({e}). Download it manually from {url} and save it as {dest}") from e
    return dest


# ---------------- OpenStreetMap (OSMnx) ----------------
def load_osmnx(name: str, places) -> Graph:
    import osmnx as ox

    print(f"  querying OpenStreetMap for {places} (this can take a few minutes)")
    G = ox.graph_from_place(places, network_type="drive", simplify=True)
    G = ox.truncate.largest_component(G, strongly=True)
    ids = {osm_id: i for i, osm_id in enumerate(G.nodes)}
    coords = [(G.nodes[o]["x"], G.nodes[o]["y"]) for o in ids]          # (lon, lat)
    edges = [(ids[u], ids[v], float(d["length"])) for u, v, d in G.edges(data=True)]  # metres
    return build_graph(name, len(ids), edges, coords, directed=True)


# ---------------- DIMACS (9th Challenge) ----------------
def parse_dimacs_gr(path: Path):
    n, edges = 0, []
    with gzip.open(path, "rt") as f:
        for line in f:
            if line.startswith("p"):
                n = int(line.split()[2])
            elif line.startswith("a"):
                _, u, v, w = line.split()
                edges.append((int(u) - 1, int(v) - 1, float(w)))
    return n, edges


def parse_dimacs_co(path: Path, n: int):
    coords = [(0.0, 0.0)] * n
    with gzip.open(path, "rt") as f:
        for line in f:
            if line.startswith("v"):
                _, i, x, y = line.split()
                coords[int(i) - 1] = (int(x) / 1e6, int(y) / 1e6)       # micro-degrees -> degrees
    return coords


def load_dimacs(region: str, kind: str) -> Graph:
    """region: 'NY' or 'FLA'; kind: 'd' (distance) or 't' (travel time)."""
    gr = _download(DIMACS_BASE.format(kind=kind, region=region, ext="gr"),
                   RAW / f"USA-road-{kind}.{region}.gr.gz")
    co = _download(DIMACS_BASE.format(kind="d", region=region, ext="co"),
                   RAW / f"USA-road-d.{region}.co.gz")
    n, edges = parse_dimacs_gr(gr)
    coords = parse_dimacs_co(co, n)
    g = build_graph(f"dimacs-{region.lower()}-{kind}", n, edges, coords, directed=True)
    return g.largest_component()


# ---------------- Non-road graphs ----------------
def load_snap() -> Graph:
    path = _download(SNAP_URL, RAW / "soc-Slashdot0811.txt.gz")
    ids, edges = {}, []
    with gzip.open(path, "rt") as f:
        for line in f:
            if line.startswith("#"):
                continue
            a, b = line.split()
            for x in (a, b):
                if x not in ids:
                    ids[x] = len(ids)
            edges.append((ids[a], ids[b], 1.0))
    g = build_graph("snap-slashdot", len(ids), edges, None, directed=False)  # treated as undirected, unit weights
    return g.largest_component()


def make_random_like(ref: Graph, seed: int = 42) -> Graph:
    """Erdos-Renyi G(n, m) with the same node and undirected-edge count as `ref`, unit weights."""
    rng = random.Random(seed)
    n, m = ref.n, ref.m // 2
    seen = set()
    while len(seen) < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v:
            seen.add((min(u, v), max(u, v)))
    g = build_graph("random-er", n, [(u, v, 1.0) for u, v in seen], None, directed=False)
    return g.largest_component()
