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

def EventTick(): # эта функция, которая срабатывает каждый кадр
    print("tick:", engine.clock.get_fps())
    i.Rotate(1)



engine.EventTick.connection_functions.append(EventTick) # делаем так,что-бы EventTick() вызывался каждый кадр
engine.Run() # запускаем движок