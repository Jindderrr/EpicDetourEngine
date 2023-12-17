# Tech Demo of Epic Detour Engine

import EpicDetourEngine as engine
import pygame

bricksM1 = engine.Material("textures/texture1.png")
bricksM2 = engine.Material("textures/texture4.jpg")
steelM3 = engine.Material("textures/texture3.jpg")
smalltilesM4 = engine.Material("textures/texture7.png")

class door(engine.Actor):
    def __init__(self, originLocation=(0, 0), LocationZ=0, Height=3, Rotation=0, thickness=0.25, a=2, Material=engine.CLASSIC_MATERIAL, da=2):
        door = engine.Item()
        door.addWall(engine.Wall(((0, thickness / 2), (a, thickness / 2)), height=Height, Material=Material))
        door.addWall(engine.Wall(((0, -thickness / 2), (a, -thickness / 2)), height=Height, Material=Material))
        door.addWall(engine.Wall(((a, thickness / 2), (a, -thickness / 2)), height=Height, Material=Material))
        super().__init__(originLocation, LocationZ, Rotation, {'door': door})
        ibd = engine.InBoxDetector((a/2, 0), (a, 7))
        self.add({'detctor': ibd})
        self.a = a
        self.open = False
        self.door_dx = 0
        self.da = da

    def EventTick(self):
        all = [t.Tags for t in self.getElem('detctor')[0].AllInBox() if 'player' in t.Tags]
        if len(all) > 0: self.open = True
        else: self.open = False

        if self.open:
            if self.door_dx > -self.da:
                self.door_dx -= 3 * engine.WorldDeltaSeconds
            if self.door_dx < -self.da:
                self.door_dx = -self.da
            self.setElementLocalLocation('door', (self.door_dx, 0))
        else:
            if self.door_dx < 0:
                self.door_dx += 3 * engine.WorldDeltaSeconds
            if self.door_dx > 0:
                self.door_dx = 0
            self.setElementLocalLocation('door', (self.door_dx, 0))
        self.Update()

player = engine.Base_FirstPersonCharacter()
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
# wall1 = engine.Wall(PointsLocation=((-2, 2), (5, 2)), height=3, Material=steelM3)
# engine.Wall(PointsLocation=((-5.4, 2), (-2, 2)), height=3, Material=bricksM2)
#
# engine.Wall(PointsLocation=((-5.4, 2), (-5.4, -1.5)), height=3, Material=bricksM2)
# engine.Wall(PointsLocation=((5, 2), (5, -0.2)), height=3, Material=engine.Material((0, 100, 0)))
# engine.Wall(PointsLocation=((5, -0.2), (4.8, -0.2)), height=3, Material=engine.Material((190, 45, 0)))
# engine.Wall(PointsLocation=((4.8, -0.2), (4.8, -1.5)), height=3 ,Material=engine.Material("textures/texture2.png"))
# engine.Wall(PointsLocation=((-2, -3.5), (4, -3.5)), height=3, Material=bricksM2)
# engine.Wall(PointsLocation=((4, -3.5), (4, -1)), height=3, Material=bricksM2)
# engine.Wall(PointsLocation=((-2, -1.2), (-4, -1.2)), height=3, Material=bricksM2)
#
# engine.Wall(PointsLocation=((-2, 2), (-2, 0)), height=2, Material=bricksM1)
# engine.Wall(PointsLocation=((-2, 0), (-2.25, 0)), height=2, Material=bricksM1)
# engine.Wall(PointsLocation=((-2.25, 2), (-2.25, 0)), height=2, Material=bricksM1)
# print(len(engine.AllWalls))
#
# engine.SpriteFaceToCamera(Height=2, Material=engine.Material("textures/texture6.png"), OrigineLocation=(1, 0.5), LocationZ=0)
# engine.SpriteFaceToCamera(Height=0.5, Material=engine.Material("textures/lamp0.png"), OrigineLocation=(1, 0), LocationZ=2.5)
#
# engine.Wall(PointsLocation=((-2, -1.2), (-2, -10)), height=3, Material=bricksM2)
# engine.Wall(PointsLocation=((-2, -10), (-4.5, -10)), height=3, Material=bricksM2)
# engine.Wall(PointsLocation=((-7, -10), (-5.5, -10)), height=3, Material=bricksM2)
# engine.Wall(PointsLocation=((-7, -10), (-7, -5)), height=3, Material=bricksM2)
mat = {'bricksM1': bricksM1, 'bricksM2': bricksM2, 'smalltilesM4': smalltilesM4, 'steelM3': steelM3}
r = engine.OpenOBJAsMap("./maps/map1.obj", mat)
for ue in r:
    if ue[0][0] == 'door1':
        print(ue[0])
        print(float(ue[0][1]))
        door(ue[1], float(ue[0][1]), float(ue[0][2]), float(ue[0][3]), float(ue[0][4]), float(ue[0][5]), mat[ue[0][6]], float(ue[0][7]))

tr = engine.Tracker(("player",))
def EventTick(): # эта функция, которая срабатывает каждый кадр, до отрисовки
    # print("tick:", engine.clock.get_fps())
    tr.LocationX = engine.ActiveCamera.LocationX
    tr.LocationY = engine.ActiveCamera.LocationY


def EventTickAfterRendering(): # эта функция, которая срабатывает каждый кадр, после отрисовки
    gun = pygame.image.load("textures/gun0.png")
    gun = pygame.transform.scale(gun, (320, 400))
    engine.screen.blit(gun, (engine.screen_width / 2 - 160, 300))


engine.EventTick.connection_functions.append(EventTick) # делаем так,что-бы EventTick() вызывался каждый кадр, до отрисовки
engine.EventTick.connection_functions_after_rendering.append(EventTickAfterRendering) # делаем так,что-бы EventTickAfterRendering() вызывался каждый кадр, после отрисовки
engine.Run() # запускаем движок