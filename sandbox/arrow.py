import iceberg as ice

box = ice.Rectangle(ice.Bounds.from_size(64, 64), border_thickness=0, fill_color=ice.Colors.CYAN)
ball = ice.Ellipse(rectangle=ice.Bounds.from_size(64, 64), border_thickness=0, fill_color=ice.Colors.YELLOW).background(ice.Colors.BLACK)
boxball = ice.Arrange(box, ball, gap=0, arrange_direction=ice.Arrange.Direction.HORIZONTAL).scale(10,10)

class Animation(ice.Playbook):
    def timeline(self):
        arrangement = ice.Arrange(box.pad_right(200), ball, gap=0, arrange_direction=ice.Arrange.Direction.HORIZONTAL).background(ice.Colors.BLACK)

        with arrangement:
            arrowA = ice.Arrow(
                box.relative_bounds.corners[ice.Corner.MIDDLE_RIGHT],
                ball.relative_bounds.corners[ice.Corner.MIDDLE_LEFT],
                line_path_style=ice.PathStyle(ice.Colors.WHITE, 5),
                partial_end=0.3,
            )

            arrowB = ice.Arrow(
                box.relative_bounds.corners[ice.Corner.MIDDLE_RIGHT],
                ball.relative_bounds.corners[ice.Corner.MIDDLE_LEFT],
                line_path_style=ice.PathStyle(ice.Colors.WHITE, 5),
                partial_end=1,
            )

            arrow = ice.Animated([arrowA, arrowB], 1.0)

        scene = ice.Compose(arrangement, arrow).background(ice.Colors.BLACK).scale(2)
        self.play(scene)

anim = Animation()
anim.ipython_display(display_format='gif', fps=50)
anim.combined_scene.render('sandbox/arrow.gif', fps=50)
