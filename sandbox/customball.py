from typing import Tuple

import iceberg as ice

class Ball(ice.DrawableWithChild):
    radius: float
    center: Tuple[float] = (0, 0)
    fill_color: ice.Color = ice.Colors.RED

    def setup(self):
        cx, cy = self.center
        left, top, right, bottom = (
            cx - self.radius,
            cy - self.radius,
            cx + self.radius,
            cx + self.radius,
        )
        internal_ball = ice.Ellipse(
            rectangle=ice.Bounds(left, top, right, bottom),
            fill_color=self.fill_color,
            border_thickness=0,
        ).background(ice.Colors.BLACK)

        self.set_child(internal_ball)

Ball(radius=64)
