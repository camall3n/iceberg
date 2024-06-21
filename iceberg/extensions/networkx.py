import math
from typing import List, Tuple, Union

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


def arc_path(posA: Tuple[float], posB: Tuple[float], bend: float = 0.5, angularity: float = 0.5) -> List[Tuple[float]]:
    """
    Creates a simple quadratic Bézier curve between two
    points. The curve is created so that the middle control point
    (C1) is located at the same distance from the start (C0) and
    end points(C2) and the distance of the C1 to the line
    connecting C0-C2 is *bend* times the distance of C0-C2.

    Parameters
    ----------
    posA : Tuple[float]
      Start position
    posB : Tuple[float]
      End position
    bend : float
      Curvature of the curve, where bend=0 is a straight line between the
      points, and bend=1 is a curve whose width is equal to the straight-
      line distance between its endpoints when angularity = 1.
    angularity : float
      Controls the angularity of the arc by moving the control points
      closer or farther from the endpoints. When angularity = 1 there is
      no smoothing or sharpening. Higher values will produce sharper
      curves; lower values will produce smoother curves. When angularity
      is zero, the curve is a straight line.
    """
    x1, y1 = posA
    x2, y2 = posB

    x12, y12 = (x1 + x2) / 2., (y1 + y2) / 2.  # midpoint
    dx, dy = x2 - x1, y2 - y1  # straight-line distance
    cx, cy = x12 + bend * dy, y12 - bend * dx  # control point ray intersection

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
    b, a, d, c = truncate_arc([b, a, d, c], length * (1-angularity))

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
    radius: float = 32
    scale: Union[float, str] = 'auto'
    layout: str = 'circular_layout'
    fill_color: ice.Color = ice.Colors.WHITE
    edge_color: ice.Color = ice.Colors.BLACK

    def setup(self):
        layout_fn = getattr(nx.drawing.layout, self.layout)
        nodelist = list(self.graph.nodes())
        if self.scale == 'auto':
            self.scale = self.radius * len(nodelist)
        pos = layout_fn(self.graph, scale=self.scale)
        nodes = []
        for name in nodelist:
            node = Node(radius=self.radius, center=pos[name], text=name)
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
