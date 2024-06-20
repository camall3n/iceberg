import iceberg as ice

box = ice.Rectangle(ice.Bounds.from_size(64, 64), fill_color=ice.Colors.CYAN)
ball = ice.Ellipse(rectangle=ice.Bounds.from_size(64, 64), fill_color=ice.Colors.YELLOW).background(ice.Colors.BLACK)
boxball = ice.Arrange(box, ball, arrange_direction=ice.Arrange.Direction.HORIZONTAL).scale(10,10)
boxball.render('sandbox/boxball.png')
boxball
