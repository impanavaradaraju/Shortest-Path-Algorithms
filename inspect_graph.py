
import pickle

# Load Toronto graph
with open("data/processed/toronto.pkl", "rb") as f:
    G = pickle.load(f)

print("=" * 50)
print("TORONTO ROAD NETWORK")
print("=" * 50)

# Basic information
print("Dataset name:", G.name)
print("Number of nodes:", G.n)
print("Number of directed arcs:", G.m)
print("Directed:", G.directed)
print("Coordinates available:", G.coords is not None)

# Inspect first 5 nodes
print("\nFIRST 5 NODES")
for node in range(5):
    print(f"Node {node}:")
    print("  Coordinates:", G.coords[node])
    print("  Connections:", G.adj[node][:5])

# Inspect first 5 edges
print("\nFIRST 5 EDGES")
for u in range(5):
    for v, weight in G.adj[u][:2]:
        print(f"{u} -> {v}, distance = {weight}")

# Calculate weight statistics
weights = [
    weight
    for neighbors in G.adj
    for _, weight in neighbors
]

print("\nEDGE WEIGHT STATISTICS")
print("Minimum:", min(weights))
print("Maximum:", max(weights))
print("Average:", sum(weights) / len(weights))

print("\nGraph summary:")
print(G.summary())
