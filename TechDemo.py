import EpicDetourEngine as engine

engine.Base_FirstPersonCharacter()
i = engine.Item((2, 0.5))
wall1 = engine.Wall(((0.2,0.2), (0.2,-0.2)), (100,100,100))
wall2 = engine.Wall(((0.2,-0.2), (-0.2,-0.2)), (150,150,150))
wall3 = engine.Wall(((-0.2,-0.2), (-0.2,0.2)), (100,100,100))
wall4 = engine.Wall(((-0.2,0.2), (0.2,0.2)), (150,150,150))
i.addWall(wall1)
i.addWall(wall2)
i.addWall(wall3)
i.addWall(wall4)
engine.walls += (wall1, wall2, wall3, wall4)
i.Rotate()
engine.walls += engine.WallBox((0, -2), 0.6, (0, 200, 150))
wall1 = engine.Wall(PointsLocation=((-2, 2), (5, 2)))
wall2 = engine.Wall(PointsLocation=((5, 2), (5, -0.2)), Color=(0, 100, 0))
wall3 = engine.Wall(PointsLocation=((5, -0.2), (4.8, -0.2)), Color=(190, 45, 0))
wall4 = engine.Wall(PointsLocation=((4.8, -0.2), (4.8, -1.5)), Color=(200, 50, 0))
wall5 = engine.Wall(PointsLocation=((-2, 2), (-2, -1)), Color=(0, 0, 0))
engine.walls += [wall1, wall2, wall3, wall4, wall5]
for i in range(0):
    engine.walls.append(engine.Wall(PointsLocation=((-1, 2), (-1, -1)), Color=(0, 0, 0)))
print(len(engine.walls))

def EventTick(): # эта функция, которая срабатывает каждый кадр
    print("tick:", engine.clock.get_fps())
    i.Rotate(1)



engine.EventTick.connection_functions.append(EventTick) # делаем так,что-бы EventTick() вызывался каждый кадр
engine.Run() # запускаем движок