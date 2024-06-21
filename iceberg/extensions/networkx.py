import collections
import itertools
import math
from typing import List, Tuple

import iceberg as ice
import networkx as nx

def truncate_arc(path: List[Tuple[float]], truncation: float) -> List[Tuple[float]]:
    """
    Truncate a Bézier arc by moving each endpoint along a straight line
    towards its control point, for an amount equal to truncation.

    Parameters
    ----------
    path : List[Tuple[float]]
      Bézier arc
    truncation : float
      The amount by which to truncate the line
    """
    a, b, c, d = path

    # vector from A to B
    ab_x = b[0] - a[0]
    ab_y = b[1] - a[1]
    ab_length = math.sqrt(ab_x**2 + ab_y**2)
    new_a = (a[0] + truncation * ab_x/ab_length, a[1] + truncation * ab_y/ab_length)

    # vector from D to C
    dc_x = c[0] - d[0]
    dc_y = c[1] - d[1]
    dc_length = math.sqrt(dc_x**2 + dc_y**2)
    new_d = (d[0] + truncation * dc_x/dc_length, d[1] + truncation * dc_y/dc_length)

    return (new_a, b, c, new_d)

def arc_path(posA: Tuple[float], posB: Tuple[float], rad: float = 0.) -> List[Tuple[float]]:
    """
    Creates a simple quadratic Bézier curve between two
    points. The curve is created so that the middle control point
    (C1) is located at the same distance from the start (C0) and
    end points(C2) and the distance of the C1 to the line
    connecting C0-C2 is *rad* times the distance of C0-C2.

    Parameters
    ----------
    posA : Tuple[float]
      Start position
    posB : Tuple[float]
      End position
    rad : float
      Curvature of the curve, where rad=0 is a straight line between the
      points, and rad=1 is a curve whose width is equal to the straight-
      line distance between its endpoints.
    """
    x1, y1 = posA
    x2, y2 = posB
    x12, y12 = (x1 + x2) / 2., (y1 + y2) / 2.
    dx, dy = x2 - x1, y2 - y1

    f = rad

    cx, cy = x12 + f * dy, y12 - f * dx

    # move control points halfway towards endpoints for smoothness
    a, b, c, d = [
        (x1, y1),
        (cx, cy),
        (cx, cy),
        (x2, y2)
    ]
    ab_x = b[0] - a[0]
    ab_y = b[1] - a[1]
    length = math.sqrt(ab_x**2 + ab_y**2)
    b, a, d, c = truncate_arc([b, a, d, c], length/2)

    vertices = [a, b, c, d]
    return vertices


class Node(ice.DrawableWithChild):
    radius: float
    center: Tuple[float] = (0, 0)
    text: str = None
    fill_color: ice.Color = ice.Colors.WHITE
    border_color: ice.Color = ice.Colors.BLACK

    def setup(self):
        ball = ice.Ellipse(
            rectangle=ice.Bounds(center=self.center, size=[self.radius * 2] * 2),
            fill_color=self.fill_color,
            border_color=self.border_color,
            border_thickness=0,
            border_radius=1,
        ).background(ice.Colors.TRANSPARENT)

        if self.text is not None:
            text = ice.SimpleText(text=str(self.text), font_style=ice.FontStyle('Arial', color=ice.Colors.BLACK))
            ball = ball.next_to(text)

        self.set_child(ball)


class NetworkXGraph(ice.DrawableWithChild):
    graph: nx.Graph
    pos: Tuple[float]
    radius: float = 32
    fill_color: ice.Color = ice.Colors.WHITE
    edge_color: ice.Color = ice.Colors.BLACK

    def setup(self):
        nodelist = list(self.graph.nodes())
        nodes = []
        for name in nodelist:
            node = Node(radius=self.radius, center=self.pos[name], text=name)
            nodes.append(node)

        edgelist = list(self.graph.edges)

        edges = []
        for start, end in edgelist:
            # grab edge data and compute number of edges
            edge_data = self.graph.get_edge_data(start, end)
            backward_edge_data = self.graph.get_edge_data(end, start, default=[])
            n_edges = len(edge_data) + len(backward_edge_data)

            # build smooth curve if there's an edge in each direction
            curvature = 0.15 * (n_edges - 1)
            path = truncate_arc(arc_path(pos[start], pos[end], curvature), truncation=self.radius)
            bezier = ice.CubicBezier(path)
            arrow = ice.ArrowPath(
                bezier,
                arrow_head_style=ice.ArrowHeadStyle.FILLED_TRIANGLE,
                head_length=0.2*self.radius,
            )

            # make a text label containing the edge weight
            text = ice.Text(
                text=str(edge_data['weight']),
                font_style=ice.FontStyle('Arial', color=ice.Colors.BLACK),
                align=ice.primitives.text.Text.Align.CENTER,
            )
            # Compute a nice position for the text, near the ending control point
            w, h = text.bounds.size
            text_pos = path[-2][0] - w/2, path[-2][1] - h/2
            text = text.move_to(*text_pos).pad(2).background(ice.Color(1,1,1,0.8))

            arrow_with_text = arrow.add(text)
            edges.append(arrow_with_text)

        composition = ice.Compose(nodes + edges)

        self.set_child(composition)


G = nx.DiGraph()
G.add_edge(1, 3, weight=3)
G.add_edge(3, 4, weight=4)
G.add_edge(2, 5, weight=2)
G.add_edge(1, 2, weight=4)
G.add_edge(2, 1, weight=2)
G.add_edge(1, 4, weight=1)
G.add_edge(2, 3, weight=1)
G.add_edge(5, 6, weight=1)
G.add_edge(6, 4, weight=1)
pos = nx.circular_layout(G, scale=200)
ice.Compose(NetworkXGraph(graph=G, pos=pos)).pad(10)


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
