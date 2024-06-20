import iceberg as ice

rect = ice.Rectangle(ice.Bounds.from_size(64, 64), fill_color=ice.Colors.CYAN)
ball = ice.Ellipse(rectangle=ice.Bounds.from_size(64, 64), fill_color=ice.Colors.YELLOW).background(ice.Colors.BLACK)
boxball = ice.Arrange(rect, ball, arrange_direction=ice.Arrange.Direction.HORIZONTAL).scale(10,10)
boxball.render('boxball.png')
boxball
