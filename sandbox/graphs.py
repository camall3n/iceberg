import iceberg as ice
from iceberg.extensions.networkx import NetworkXGraph, Node, arc_path
import networkx as nx

color = lambda x: ice.PathStyle(x)
ice.Compose([
    Node(center=(0,0), radius=20),
    Node(center=(100,0), radius=20),
    ice.CubicBezier(arc_path((0,0), (100,0), bend=0.5, angularity=0.5), color(ice.Colors.BLACK)),
    ice.CubicBezier(arc_path((0,0), (100,0), bend=1, angularity=0.5), color(ice.Colors.RED)),
    ice.CubicBezier(arc_path((0,0), (100,0), bend=1, angularity=1), color(ice.Colors.BLUE)),
    ice.CubicBezier(arc_path((0,0), (100,0), bend=1, angularity=2), color(ice.Colors.CYAN)),
    ice.CubicBezier(arc_path((0,0), (100,0), bend=0.5, angularity=3), color(ice.Colors.MAGENTA)),
]).pad(20)

#%%

G = nx.DiGraph()
G.add_edge(1, 3, weight=3)
G.add_edge(3, 4, weight=4)
G.add_edge(2, 5, weight=2)
G.add_edge(1, 2, weight=4)
G.add_edge(2, 1, weight=2)
G.add_edge(1, 4, weight=1)
G.add_edge(2, 3, weight=1)
G.add_edge(5, 6, weight=1)
G.add_edge(1, 5, weight=1)
G.add_edge(6, 4, weight=1)
G.add_edge(6, 3, weight=1)
G.add_edge(2, 4, weight=1)
G.add_edge(7, 5, weight=1)
G.add_edge(8, 9, weight=1)
pos = nx.circular_layout(G, scale=200)
ice.Compose(NetworkXGraph(graph=G)).pad(10)


#%% Built-in NetworkX draw
options = {
    "font_size": 12,
    "node_size": 1000,
    "node_color": "white",
    "edgecolors": "black",
    "linewidths": 1,
    "width": 1,
}
nx.draw_networkx(G, pos=pos, **options)

#%% Draw function adapted from NetworkX docs
# https://networkx.org/documentation/latest/auto_examples/drawing/plot_multigraphs.html#sphx-glr-auto-examples-drawing-plot-multigraphs-py

def draw_labeled_multigraph(G, attr_name, ax=None):
    """
    Length of connectionstyle must be at least that of a maximum number of edges
    between pair of nodes. This number is maximum one-sided connections
    for directed graph and maximum total connections for undirected graph.
    """
    # Works with arc3 and angle3 connectionstyles
    connectionstyle = [f"arc3,rad={r}" for r in [0.15, 0.3, 0.45, 0.6]]
    # connectionstyle = [f"angle3,angleA={r}" for r in it.accumulate([30] * 4)]

    pos = nx.circular_layout(G)
    nx.draw_networkx_nodes(G, pos, node_color="white", edgecolors="black", ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=12, ax=ax)
    nx.draw_networkx_edges(
        G, pos, edge_color="black", connectionstyle=connectionstyle, ax=ax
    )

    labels = {
        tuple(edge): f"{attrs[attr_name]}"
        for *edge, attrs in G.edges(data=True)
    }
    nx.draw_networkx_edge_labels(
        G,
        pos,
        labels,
        connectionstyle=connectionstyle,
        label_pos=0.3,
        font_color="black",
        bbox={"alpha": 0},
        ax=ax,
    )

draw_labeled_multigraph(G, 'weight')
