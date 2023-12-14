# Tech Demo of Epic Detour Engine

import EpicDetourEngine as engine
import pygame

engine.Base_FirstPersonCharacter()
i = engine.Item((2, 0.5))
#wall1 = engine.Wall(((0.2, 0.2), (0.2, -0.2)), 3,engine.Material((100, 100, 100)))
#wall2 = engine.Wall(((0.2, -0.2), (-0.2, -0.2)), 3, engine.Material((150, 150, 150)))
#wall3 = engine.Wall(((-0.2, -0.2), (-0.2, 0.2)), 3, engine.Material((100, 100, 100)))
#wall4 = engine.Wall(((-0.2, 0.2), (0.2, 0.2)), 3, engine.Material((150, 150, 150)))
#i.addWall(wall1)
#i.addWall(wall2)
#i.addWall(wall3)
#i.addWall(wall4)
#i.Rotate()
bricks_m1 = engine.Material("textures/texture1.png")
bricks_m2 = engine.Material("textures/texture5.jpg")
steel_m3 = engine.Material("textures/texture3.jpg")
wall1 = engine.Wall(PointsLocation=((-2, 2), (5, 2)), height=3, Material=steel_m3)
engine.Wall(PointsLocation=((-5.4, 2), (-2, 2)), height=3, Material=bricks_m2)

engine.Wall(PointsLocation=((-5.4, 2), (-5.4, -1.5)), height=3, Material=bricks_m2)
engine.Wall(PointsLocation=((5, 2), (5, -0.2)), height=3, Material=engine.Material((0, 100, 0)))
engine.Wall(PointsLocation=((5, -0.2), (4.8, -0.2)), height=3, Material=engine.Material((190, 45, 0)))
engine.Wall(PointsLocation=((4.8, -0.2), (4.8, -1.5)), height=3 ,Material=engine.Material("textures/texture2.png"))
engine.Wall(PointsLocation=((-2, -1.2), (-2, -3.5)), height=3, Material=bricks_m2)
engine.Wall(PointsLocation=((-2, -3.5), (4, -3.5)), height=3, Material=bricks_m2)
engine.Wall(PointsLocation=((4, -3.5), (4, -1)), height=3, Material=bricks_m2)
engine.Wall(PointsLocation=((-2, -1.2), (-4, -1.2)), height=3, Material=bricks_m2)

engine.Wall(PointsLocation=((-2, 2), (-2, 0)), height=2, Material=bricks_m1)
engine.Wall(PointsLocation=((-2, 0), (-2.25, 0)), height=2, Material=bricks_m1)
engine.Wall(PointsLocation=((-2.25, 2), (-2.25, 0)), height=2, Material=bricks_m1)
print(len(engine.AllWalls))

engine.SpriteFaceToCamera(Height=2, Material=engine.Material("textures/texture6.png"), OrigineLocation=(1, 0.5), LocationZ=0)

def EventTick(): # эта функция, которая срабатывает каждый кадр, до отрисовки
    # print("tick:", engine.clock.get_fps())
    pass

def EventTickAfterRendering(): # эта функция, которая срабатывает каждый кадр, после отрисовки
    gun = pygame.image.load("textures/gun0.png")
    gun = pygame.transform.scale(gun, (320, 400))
    engine.screen.blit(gun, (engine.screen_width / 2 - 160, 300))


engine.EventTick.connection_functions.append(EventTick) # делаем так,что-бы EventTick() вызывался каждый кадр, до отрисовки
engine.EventTick.connection_functions_after_rendering.append(EventTickAfterRendering) # делаем так,что-бы EventTickAfterRendering() вызывался каждый кадр, после отрисовки
engine.Run() # запускаем движок