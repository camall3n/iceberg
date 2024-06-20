from typing import Tuple

import iceberg as ice
import networkx as nx

class Node(ice.DrawableWithChild):
    radius: float
    center: Tuple[float] = (0, 0)
    text: str = None
    fill_color: ice.Color = ice.Colors.WHITE
    border_color: ice.Color = ice.Colors.BLACK

    def setup(self):
        cx, cy = self.center
        left, top, right, bottom = (
            cx - self.radius,
            cy - self.radius,
            cx + self.radius,
            cy + self.radius,
        )
        ball = ice.Ellipse(
            rectangle=ice.Bounds(left, top, right, bottom),
            fill_color=self.fill_color,
            border_color=self.border_color,
            border_thickness=0,
            border_radius=1,
        ).background(ice.Colors.TRANSPARENT)

        if self.text is not None:
            text = ice.SimpleText(text=self.text, font_style=ice.FontStyle('Arial', color=ice.Colors.BLACK))
            ball = ball.next_to(text)

        self.set_child(ball)

Node(radius=32, text='foo')

#%%

class NetworkXGraph(ice.DrawableWithChild):
    graph: nx.Graph
    radius: float = 32
    fill_color: ice.Color = ice.Colors.WHITE
    edge_color: ice.Color = ice.Colors.BLACK

    def setup(self):
        node_positions = nx.arf_layout(self.graph, scaling=self.radius)
        nodes = []
        for name, position in node_positions.items():
            node = Node(radius=self.radius, center=2*position, text=name)
            nodes.append(node)

        composition = ice.Compose(nodes)
        self.set_child(composition)

G = nx.Graph()
G.add_edge("A", "B", weight=4)
G.add_edge("B", "D", weight=2)
G.add_edge("A", "C", weight=3)
G.add_edge("C", "D", weight=4)
NetworkXGraph(graph=G)
