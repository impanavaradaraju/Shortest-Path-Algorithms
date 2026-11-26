# DS8001 Shortest-Path Project (Group 24)

Steps 1-2: load graphs and validate our own Dijkstra.

## Setup (VS Code)
1. Open this folder in VS Code (File > Open Folder). Install the **Python** extension.
2. Terminal > New Terminal, then:
   - macOS/Linux: `python3.11 -m venv .venv && source .venv/bin/activate`
   - Windows: `py -3.11 -m venv .venv` then `.venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. Ctrl+Shift+P > "Python: Select Interpreter" > choose `.venv`.

## Run
    pytest                                              # unit tests (should pass first)
    python step1_load_graphs.py --graphs toronto        # start small
    python step2_validate_dijkstra.py --graphs toronto --pairs 100
    python step1_load_graphs.py --graphs dimacs-ny-d dimacs-ny-t snap random
    python step2_validate_dijkstra.py --graphs dimacs-ny-d snap random --pairs 50
    python step1_load_graphs.py --graphs gta dimacs-fla-d dimacs-fla-t   # large, run last

Graphs are cached in `data/processed/*.pkl`; re-runs skip them (`--force` rebuilds).

## Layout
- `sp/graph.py` shared Graph structure (all algorithms use it) 
- `sp/loaders.py` OSMnx, DIMACS, SNAP, random graph loaders
- `sp/dijkstra.py` Dijkstra with settled-node and heap-operation counters
- `tests/` pytest checks against NetworkX
