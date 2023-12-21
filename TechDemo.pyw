# Tech Demo of Epic Detour Engine

import EpicDetourEngine as engine
import pygame, random
import numpy as np

bricksM1 = engine.Material("textures/texture1.png")
bricksM2 = engine.Material("textures/texture4.jpg")
steelM3 = engine.Material("textures/texture3.jpg")
smalltilesM4 = engine.Material("textures/texture7.png")
lamp0 = engine.Material("textures/lamp0.png")
exit1 = engine.Material("textures/texture9.png")
gunonwall = engine.Material("textures/texture15m.jpg")
betonM = engine.Material("textures/texture16.jpg")
closedM1 = engine.Material("textures/texture17.jpg")
canwall = engine.Material("textures/texture18.jpg")

class door(engine.Actor):
    def __init__(self, originLocation=(0, 0), LocationZ=0, Height=3, Rotation=0, thickness=0.25, a=2, Material=engine.CLASSIC_MATERIAL, da=2):
        door = engine.Item()
        door.addWall(engine.Wall(((0, thickness / 2), (a, thickness / 2)), height=Height, Material=Material, collision=False))
        door.addWall(engine.Wall(((0, -thickness / 2), (a, -thickness / 2)), height=Height, Material=Material, collision=False))
        door.addWall(engine.Wall(((a, thickness / 2), (a, -thickness / 2)), height=Height, Material=Material, collision=False))
        super().__init__(originLocation, LocationZ, Rotation, {'door': door})
        ibd = engine.InBoxDetector((a/2, 0), (a, 7))
        self.add({'detctor': ibd})
        self.a = a
        self.open = False
        self.door_dx = 0
        self.da = da

    def EventTick(self):
        all = [t.Tags for t in self.getElem('detctor')[0].AllInBox() if 'player' in t.Tags]
        print("---")
        print(all)
        print(self)
        print(self.open)

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


class enemy(engine.Base.Character):
    def __init__(self, originLocation=(0, 0)):
        self.te = [engine.Material("textures/texture6.png"), engine.Material("textures/texture6st.png"), engine.Material("textures/texture6d1-1.png"), engine.Material("textures/texture6df1.png")]
        # self.te = [engine.Material("textures/texture8.png"), engine.Material("textures/texture8.png"),
        #            engine.Material("textures/texture6d1-1.png"), engine.Material("textures/texture6df1.png")]
        ftc = engine.SpriteFaceToCamera(Height=2, Material=self.te[0], collision=True)
        super().__init__(originLocation=originLocation)
        self.add({'ftc': ftc})
        self.fire = False
        self.tls = -1
        self.hp = 100


    def EventTick(self):
        lt = engine.LineTrace(self.getLocation(), player.getLocation(), engine.AllWallCollision)
        b = False
        for w in lt:
            if w[0] != self.getElem('ftc')[0].c_surface:
                b = True
        if self.hp > 25:
            if not b:
                self.fire = True
            else:
                self.tls = -0.2
            self.tls += engine.WorldDeltaSeconds
            if self.tls > 0.05:
                self.getElem('ftc')[0].surface.Material = self.te[0]
            if self.fire and self.tls > 0.2:
                player.hp -= random.randint(2, 4)
                self.tls = 0
                self.getElem('ftc')[0].surface.Material = self.te[1]
        else:
            if self.hp > 0:
                self.getElem('ftc')[0].surface.Material = self.te[2]
                self.hp -= engine.WorldDeltaSeconds * 3
            else:
                self.getElem('ftc')[0].surface.Material = self.te[3]
                if self in AllEnemies:
                    AllEnemies.pop(AllEnemies.index(self))
        super().EventTick()

class player(engine.Base.FirstPersonCharacter):
    def __init__(self):
        super().__init__()
        GunSize = 4
        self.gun = pygame.image.load("textures/gun2_dg.png")
        self.gun = pygame.transform.scale(self.gun, (self.gun.get_width() // GunSize, self.gun.get_height() // GunSize))
        self.gun = pygame.transform.scale(self.gun, (engine.screen_width, engine.screen_height))
        self.gunst = pygame.image.load("textures/gun2st_dg.png")
        self.gunst = pygame.transform.scale(self.gunst, (self.gun.get_width() // GunSize, self.gun.get_height() // GunSize))
        self.gunst = pygame.transform.scale(self.gunst, (engine.screen_width, engine.screen_height))
        self.gun_p = [pygame.image.load("textures/gun2p0.png"), pygame.image.load("textures/gun2p1.png"), pygame.image.load("textures/gun2p2.png")]
        for n, p in enumerate(self.gun_p):
            self.gun_p[n] = pygame.transform.scale(pygame.transform.scale(p, (self.gun.get_width() // GunSize, self.gun.get_height() // GunSize)), (engine.screen_width, engine.screen_height))
        self.hp = 100
        tr = engine.Tracker(("player"))
        self.add({'tracker': tr})
        self.time_to_last_shot = 1
        self.p = False
        self.p_time = 0
        self.p_img = [pygame.image.load("textures/patron1.png")]
        self.num_patron = 14
        self.num_patron_max = 14
        self.aim = pygame.image.load("textures/aim.png")

    def _shot(self):
        camera_v = engine.RotationToVector(self.getElem('camera')[0].Rotation)
        camera_v = camera_v[0] * 100, camera_v[1] * 100
        s = engine.LineTrace((self.LocationX, self.LocationY), camera_v, collide_walls=engine.AllWallCollision)
        for en in AllEnemies:
            if en.getElem('ftc')[0].c_surface == s[0][0]:
                en.hp -= random.randint(20, 75)
                if en.hp <= 0:
                    engine.AllWallCollision.pop(engine.AllWallCollision.index(en.getElem('ftc')[0].c_surface))

    def EventTickAfterRendering(self):
        self.time_to_last_shot += engine.WorldDeltaSeconds
        if pygame.key.get_pressed()[pygame.K_r] and not self.p:
            self.p = True
            self.p_time = 0
        if pygame.mouse.get_pressed()[0] and self.time_to_last_shot > 0.35 and not self.p and self.num_patron > 0:
            self.time_to_last_shot = 0
            self._shot()
            self.num_patron -= 1
        if not self.p:
            if self.time_to_last_shot < 0.2:
                if not self.p:
                    engine.screen.blit(self.gunst, (0, 0))
            else:
                engine.screen.blit(self.gun, (0, 0))
        else:
            self.p_time += engine.WorldDeltaSeconds
            if self.p_time <= 0.2:
                engine.screen.blit(self.gun, (0, 0))
            elif 0.2 < self.p_time <= 0.5:
                engine.screen.blit(self.gun_p[2], (0, 0))
            elif 0.5 < self.p_time <= 0.8:
                engine.screen.blit(self.gun_p[0], (0, 0))
            elif 0.8 < self.p_time <= 1.3:
                engine.screen.blit(self.gun_p[1], (0, 0))
            #elif 1.4 < self.p_time <= 1.4:
            #    engine.screen.blit(self.gun_p[0], (0, 0))
            elif 1.3 < self.p_time <= 1.6:
                engine.screen.blit(self.gun_p[2], (0, 0))
                #engine.screen.blit(self.gun, (0, 0))
            else:
                self.num_patron= self.num_patron_max
                self.p = False
                engine.screen.blit(self.gun, (0, 0))
        font = pygame.font.Font(None, 56)
        text = font.render(str(self.hp), True, (255, 50, 50))
        engine.screen.blit(text, (10, engine.screen_height - 55))
        for n in range(0, self.num_patron):
            engine.screen.blit(self.p_img[0], (engine.screen_width - n * 8 - 12, engine.screen_height-16))
        engine.screen.blit(self.aim, ((engine.screen_width - 32) / 2, (engine.screen_height - 32) / 2))

class credits:
    def __init__(self, black=0):
        self.black = black
        engine.EventTick.connection_functions_after_rendering.append(self.EventTick)
        self.y = 0

    def EventTick(self):
        print("da")
        self.y -= engine.WorldDeltaSeconds * 14
        if self.black < 255: self.black += engine.WorldDeltaSeconds * 100
        if self.black > 255: self.black = 255
        color = (0, 0, 0, self.black)
        s = pygame.Surface((engine.screen_width, engine.screen_height), pygame.SRCALPHA)
        pygame.draw.rect(s, color, (0, 0, engine.screen_width, engine.screen_height))
        engine.screen.blit(s, (0, 0))
        cr = ('Автор движка: Слизков Максим', 'Геймдизайн: Слизков Максим', 'Level-дизайн: Слизков Максим', '3D-моделирование: Слизков Максим', 'Искуственный интелект: Слизков Максим', 'UI-дизай: Слизков Максим', 'Проджект менеджмент: Слизков Максим')
        font = pygame.font.Font(None, 26)
        for n, s in enumerate(cr):
            text = font.render(s, True, (255, 255, 255))
            print(engine.screen_height + n * 40 - self.y)
            engine.screen.blit(text, (30, engine.screen_height + n * 34 + self.y))

player = player()
player.LocationX = -13
player.LocationY = 25
AllEnemies = []
AllEnemies.append(enemy((-4, 8.5)))
AllEnemies.append(enemy((-3.2, 10)))
AllEnemies.append(enemy((-4, 22)))
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
mat = {'bricksM1': bricksM1, 'bricksM2': bricksM2, 'smalltilesM4': smalltilesM4, 'steelM3': steelM3, 'lamp0': lamp0, 'exit': exit1, 'gunonwall': gunonwall, 'gunonwall': gunonwall, 'betonM': betonM, 'closedM1': closedM1, 'canwall': canwall}
r = engine.OpenOBJAsMap("./maps/map2.obj", mat)
for ue in r:
    if ue[0][0] == 'door1':
        door(ue[1], float(ue[0][1]), float(ue[0][2]), float(ue[0][3]), float(ue[0][4]), float(ue[0][5]), mat[ue[0][6]], float(ue[0][7]))

#tr = engine.Tracker(("player",))
start_credits = False
def EventTick(): # эта функция, которая срабатывает каждый кадр, до отрисовки
    pass
    global start_credits
    print(len(AllEnemies))
    if len(AllEnemies) == 0 and not start_credits:
        credits()
        start_credits = True


def EventTickAfterRendering(): # эта функция, которая срабатывает каждый кадр, после отрисовки
    pass


engine.EventTick.connection_functions.append(EventTick) # делаем так,что-бы EventTick() вызывался каждый кадр, до отрисовки
engine.EventTick.connection_functions_after_rendering.append(EventTickAfterRendering) # делаем так,что-бы EventTickAfterRendering() вызывался каждый кадр, после отрисовки
engine.Run() # запускаем движок