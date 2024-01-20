# NuclearNight by Maxim Slizkov at 20.01.2024

import EpicDetourEngine as engine
import pygame, random

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
M_map2_armory = engine.Material("textures/map2/texture_armory.jpg")
M_map2_grid = engine.Material("textures/map2/texture_grid.png")
M_map2_blood1 = engine.Material("textures/map2/texture_blood1.png")
gun0m = engine.Material('textures/gun0_loot.png')

AllEnemies = []

class Actor(engine.Actor):
    def add(self, Elements):
        r = super().add(Elements)
        for elem in r:
            if type(Elements[elem]) == UsableWall:
                self.AllElements[elem] = [Elements[elem], (Elements[elem].Location[0], Elements[elem].Location[1], Elements[elem].Rotation)]

    def setElementLocalLocation(self, name, Location = (0, 0)):
        if super().setElementLocalLocation(name, Location = (0, 0)) == 'sam davay':
            self.AllElements[name][1] = (Location[0], Location[1], self.AllElements[name][1][2])
            self.Update()

    def Update(self):
        r = super().Update()
        for elem in r:
            elemRef = self.AllElements[elem][0]
            elemX, elemY = engine.RotatePointAroundPoint(self.getLocation(), (self.AllElements[elem][1][0], self.AllElements[elem][1][1]), self.Rotation)
            if type(elemRef) == UsableWall:
                elemRef.LocationX = elemX
                elemRef.LocationY = elemY
                elemRef.Rotation = self.Rotation
                elemRef.Update()

class door(engine.Actor):
    def __init__(self, originLocation=(0, 0), LocationZ=0, Height=3, Rotation=0, thickness=0.25, a=2, Material=engine.CLASSIC_MATERIAL, da=2, f1m=None, f2m=None, AutoOpen=True):
        door = engine.Item()
        if f1m != None:
            door.addWall(engine.Wall(((0, thickness / 2), (a, thickness / 2)), height=Height, Material=f1m, collision=False))
        else:
            door.addWall(engine.Wall(((0, thickness / 2), (a, thickness / 2)), height=Height, Material=Material, collision=False))
        if f2m != None:
            door.addWall(engine.Wall(((a, -thickness / 2), (0, -thickness / 2)), height=Height, Material=f2m, collision=False))
        else:
            door.addWall(engine.Wall(((a, -thickness / 2), (0, -thickness / 2)), height=Height, Material=Material, collision=False))
        door.addWall(engine.Wall(((a, thickness / 2), (a, -thickness / 2)), height=Height, Material=Material, collision=False))
        super().__init__(originLocation, LocationZ, Rotation, {'door': door})
        ibd = engine.InBoxDetector((a/2, 0), (a, 7))
        self.add({'detector': ibd})
        self.a = a
        self.open = False
        self.door_dx = 0
        self.da = da
        self.AutoOpen = AutoOpen

    def EventTick(self):
        all = [t.Tags for t in self.getElem('detector')[0].AllInBox() if 'player' in t.Tags]
        if self.AutoOpen:
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
        #self.te = [engine.Material("textures/texture6.png"), engine.Material("textures/texture6st.png"), engine.Material("textures/texture6d1-1.png"), engine.Material("textures/texture6df1.png")]
        self.te = [engine.Material("textures/wolf4_2.png"), engine.Material("textures/wolf4.png"), engine.Material("textures/wolf5.png"), engine.Material("textures/trup.png")]
        ftc = engine.SpriteFaceToCamera(Height=2.5, Material=self.te[0], collision=True, collisionType='enemy')
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

class PlayerClass(engine.Base.FirstPersonCharacter):
    def __init__(self):
        super().__init__()
        self.CollisionWith = ('NoType', 'enemy')
        GunSize = 3
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
        self.num_patron = [0]
        self.num_patron_max = [14]
        self.aim = pygame.image.load("textures/aim.png")
        self.available_weapons = [False]
        self.selected_weapon = 0
        self.selected_actor = None

    def _shot(self):
        camera_v = engine.RotationToVector(self.getElem('camera')[0].Rotation)
        camera_v = camera_v[0] * 100 + self.LocationX, camera_v[1] * 100 + self.LocationY
        s = engine.LineTrace((self.LocationX, self.LocationY), camera_v, collide_walls=engine.AllWallCollision)
        for en in AllEnemies:
            if en.getElem('ftc')[0].c_surface == s[0][0]:
                en.hp -= random.randint(20, 75)
                if en.hp <= 0:
                    engine.AllWallCollision.pop(engine.AllWallCollision.index(en.getElem('ftc')[0].c_surface))

    def EventTickAfterRendering(self):
        if self.hp <= 0:
            self.hp = 0
            global start_credits
            if not start_credits:
                credits()
                start_credits = True
        self.time_to_last_shot += engine.WorldDeltaSeconds
        if self.available_weapons[self.selected_weapon]:
            if pygame.key.get_pressed()[pygame.K_r] and not self.p:
                self.p = True
                self.p_time = 0
            if pygame.mouse.get_pressed()[0] and self.time_to_last_shot > 0.35 and not self.p and self.num_patron[self.selected_weapon] > 0:
                self.time_to_last_shot = 0
                self._shot()
                self.num_patron[self.selected_weapon] -= 1
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
                elif 1.3 < self.p_time <= 1.6:
                    engine.screen.blit(self.gun_p[2], (0, 0))
                else:
                    if self.num_patron[self.selected_weapon] > 0:
                        self.num_patron[self.selected_weapon] = self.num_patron_max[self.selected_weapon] + 1
                    else:
                        self.num_patron[self.selected_weapon]= self.num_patron_max[self.selected_weapon]
                    self.p = False
                    engine.screen.blit(self.gun, (0, 0))
            for n in range(0, self.num_patron[self.selected_weapon]):
                engine.screen.blit(self.p_img[0], (engine.screen_width - n * 8 - 12, engine.screen_height - 16))
            engine.screen.blit(self.aim, ((engine.screen_width - 32) / 2, (engine.screen_height - 32) / 2))
            if self.num_patron[self.selected_weapon] == 0 and not self.p:
                TooltipManager.UpdateTooltip('Используйте R для перезарядки!')
        font = pygame.font.Font(None, 56)
        text = font.render(str(self.hp), True, (255, 50, 50))
        engine.screen.blit(text, (10, engine.screen_height - 55))
        v = engine.RotationToVector(self.Rotation)
        lt = engine.LineTrace(self.getLocation(), (v[0] * 2 + self.LocationX, v[1] * 2 + self.LocationY), AllUsableWalls)
        if len(lt) > 0: self.selected_actor = lt[0][0].parent
        else: self.selected_actor = None
        if self.selected_actor != None:
            if type(self.selected_actor) == map0.OpenFrontDoorButton: text = "Нажать [E]"
            else: text = "Ошибка: неопознанныей объект!"
            font = pygame.font.Font(None, 52)
            text_r = font.render(text, True, (200, 200, 200))
            engine.screen.blit(text_r, ((engine.screen_width - text_r.get_width()) / 2, (engine.screen_height - text_r.get_height()) / 1.7))
            if pygame.key.get_pressed()[pygame.K_e]:
                self.selected_actor.Use()


class Loot(engine.Actor):
    def __init__(self, Location=(0, 0), type='gun-0', material=engine.Material(), height=0.5):
        super().__init__(Location)
        detector = engine.InBoxDetector()
        sprite = engine.SpriteFaceToCamera(Height=height, Material=material, collision=False)
        self.add({'detector': detector, 'sprite': sprite})
        self.type = type


    def EventTick(self):
        all = [t.Tags for t in self.getElem('detector')[0].AllInBox() if 'player' in t.Tags]
        if len(all) > 0:
            if self.type.split('-')[0] == 'gun':
                nw = int(self.type.split('-')[1])
                player.available_weapons[nw] = True
                player.selected_weapon = nw
                player.p = True
                player.p_time = 0
            engine.EventTick.connection_functions.pop(engine.EventTick.connection_functions.index(self.EventTick))
            self.Destroy()

class credits:
    def __init__(self, black=0):
        self.black = black
        engine.EventTick.connection_functions_after_rendering.append(self.EventTick)
        self.y = 0
        player.EnableInput = False

    def EventTick(self):
        self.y -= engine.WorldDeltaSeconds * 14
        if self.black < 255: self.black += engine.WorldDeltaSeconds * 100
        if self.black > 255: self.black = 255
        color = (0, 0, 0, self.black)
        s = pygame.Surface((engine.screen_width, engine.screen_height), pygame.SRCALPHA)
        pygame.draw.rect(s, color, (0, 0, engine.screen_width, engine.screen_height))
        engine.screen.blit(s, (0, 0))
        cr = ('Автор движка: Слизков Максим', 'Геймдизайн: Слизков Максим', 'Level-дизайн: Слизков Максим', 'Персонажи: Цымбал Семён, Слизков Максим', '3D-моделирование: Слизков Максим', 'Искуственный интелект: Слизков Максим', 'UI-дизай: Слизков Максим', 'Проджект менеджмент: Слизков Максим')
        font = pygame.font.Font(None, 26)
        for n, s in enumerate(cr):
            text = font.render(s, True, (255, 255, 255))
            engine.screen.blit(text, (30, engine.screen_height + n * 34 + self.y))

class TooltipManagerClass:
    def __init__(self):
        self.text = ''
        self.time = -1
        engine.EventTick.connection_functions_after_rendering.append(self.EventTick)
        self.remembered_tooltips = []

    def EventTick(self):
        if self.time >= 0:
            if self.type == 0:
                text_color = (40, 40, 40)
                rect_color = (200, 200, 200)
            if self.type == 1:
                text_color = (20, 20, 20)
                rect_color = (200, 200, 0)
            font = pygame.font.Font(None, 24)
            text_surface = font.render(self.text, True, text_color)
            padding = 3
            tooltip_rect = pygame.Rect(text_surface.get_rect().left - padding, text_surface.get_rect().top - padding, text_surface.get_rect().width + 2 * padding, text_surface.get_rect().height + 2 * padding)
            tooltip_surface = pygame.Surface((tooltip_rect.width, tooltip_rect.height))
            tooltip_surface.fill(rect_color)
            tooltip_surface.blit(text_surface, (padding, padding))
            engine.screen.blit(tooltip_surface, (10, 10))
            self.time -= engine.WorldDeltaSeconds

    def UpdateTooltip(self, text, time=3, remember=True, type=0):
        if text not in self.remembered_tooltips:
            self.text = text
            self.time = time
            self.type = type
            if remember:
                self.remembered_tooltips.append(text)
            return True
        return False

class TooltipZone(engine.Actor):
    def __init__(self, Location, size=(1, 1), args=('Подсказка', 3, 0, 0), destroyself=True):
        detector = engine.InBoxDetector(size=size)
        super().__init__(Location)
        self.add({'detector': detector})
        self.args = args
        self.destroyself = destroyself

    def EventTick(self):
        all = [t.Tags for t in self.getElem('detector')[0].AllInBox() if 'player' in t.Tags]
        if len(all) > 0:
            TooltipManager.UpdateTooltip(*self.args)
            if self.destroyself:
                self.Destroy()

AllUsableWalls = []

class UsableWall:
    def __init__(self, Location=(0, 0), size=1, Rotation=0, addToAllUsableWalls=True, parent=None):
        if addToAllUsableWalls: AllUsableWalls.append(self)
        self.size = size
        self.Rotation = Rotation
        self.Location = Location
        self.Update()
        self.parent = parent

    def Update(self):
        self.Location1X, self.Location1Y = engine.RotatePointAroundPoint((self.Location), (-self.size / 2, 0), self.Rotation)
        self.Location2X, self.Location2Y = engine.RotatePointAroundPoint((self.Location), (self.size / 2, 0), self.Rotation)

    def getPointsLocation(self):
        return ((self.Location1X, self.Location1Y), (self.Location2X, self.Location2Y))

DoOnce_completed_functions = []
def DoOnce(function):
    if function not in DoOnce_completed_functions:
        DoOnce_completed_functions.append(function)
        function()
        return True
    return False

class Timer:
    def __init__(self, function, time):
        self.function = function
        self.time = time
        engine.EventTick.connection_functions.append(self.EventTick)

    def EventTick(self):
        self.time -= engine.WorldDeltaSeconds
        if self.time <= 0:
            self.function()
            engine.EventTick.connection_functions.pop(engine.EventTick.connection_functions.index(self.EventTick))

class Button():
    def __init__(self, text='кнопка', location=(0, 0), font=24, color=(200, 100, 50), move=False):
        self.text = text
        self.location = location
        self.font = font
        self.color = color
        self.move = move
        self.movex = 0

    def EventTick(self):
        font = pygame.font.Font(None, self.font)
        text = font.render(self.text, True, self.color)
        engine.screen.blit(text, (self.location[0] + self.movex, self.location[1]))
        hovered = self.location[0] + font.size(self.text)[0] + self.movex > pygame.mouse.get_pos()[0] > self.location[0] and self.location[1] + font.size(self.text)[1] > pygame.mouse.get_pos()[1] > self.location[1]
        if hovered and self.move:
            if self.movex < 7: self.movex += engine.WorldDeltaSeconds * 50
            else: self.movex = 7
        elif self.movex != 0:
            if self.movex > 0: self.movex -= engine.WorldDeltaSeconds * 50
            else: self.movex = 0
        return hovered and pygame.mouse.get_pressed()[0]

class map0:
    def __init__(self):
        global player
        mat = {'bricksM1': bricksM1, 'bricksM2': bricksM2, 'smalltilesM4': smalltilesM4, 'steelM3': steelM3, 'lamp0': lamp0, 'exit': exit1, 'gunonwall': gunonwall, 'gunonwall': gunonwall, 'betonM': betonM, 'closedM1': closedM1, 'canwall': canwall, 'armory': M_map2_armory, 'None': None, 'gun0': gun0m, 'grid': M_map2_grid, 'blood1': M_map2_blood1}
        r = engine.OpenOBJAsMap("./maps/map2.obj", mat)
        for ue in r:
            if ue[0][0] == 'door1':
                door(ue[1], float(ue[0][1]), float(ue[0][2]), float(ue[0][3]), float(ue[0][4]), float(ue[0][5]), mat[ue[0][6]], float(ue[0][7]), mat[ue[0][8]], mat[ue[0][9]])
            if ue[0][0] == 'enemy1':
                AllEnemies.append(enemy(ue[1]))
            if ue[0][0] == 'player':
                player = PlayerClass()
                player.LocationX = ue[1][0]
                player.LocationY = ue[1][1]
            if ue[0][0] == 'loot':
                Loot(ue[1], ue[0][1], mat[ue[0][2]], float(ue[0][3]))
            if ue[0][0] == 'tooltip':
                TooltipZone(ue[1], (float(ue[0][1]), float(ue[0][2])), (ue[0][3].replace('&', ' '), float(ue[0][4]), bool(ue[0][5]), float(ue[0][6])), bool(ue[0][7]))
        engine.EventTick.connection_functions.append(self.EventTick)
        TooltipManager.UpdateTooltip('Используйте WASD для передвижения.')
        FrontDoor = door((-1.2, -1), 0, 3, 0, 0.5, 2.4, steelM3, AutoOpen=False)
        self.OpenFrontDoorButton(door=FrontDoor, Rotation=0)

    def EventTick(self): # эта функция, которая срабатывает каждый кадр, до отрисовки, на карте map0
        global start_credits
        if len(AllEnemies) == 0 and not start_credits:
            credits()
            start_credits = True
        if player.available_weapons[0] == True:
            if TooltipManager.UpdateTooltip("Теперь надо выбираться отсюда.", type=1):
                Timer(lambda: TooltipManager.UpdateTooltip("Используйте ЛКМ для стрельбы."), 3)
                AllEnemies.append(enemy((4.6, 74.5)))
                AllEnemies.append(enemy((5.5, 75)))

    class OpenFrontDoorButton(Actor):
        def __init__(self, Location=(0, 0), Rotation=(0, 0), size=0.4, door=None):
            self.t = [engine.Material("textures/map2/texture_button_np.png"), engine.Material("textures/map2/texture_button_p.png")]
            uw = UsableWall(parent=self, size=size, Location=Location)
            sf = engine.Item()
            print(Location)
            self.sf_wall = engine.Wall(PointsLocation=((-size / 2 + Location[0], 0 + Location[1]), (size / 2 + Location[0], 0 + Location[1])), Material=self.t[0], collision=False, LocationZ=1.1, height=size)
            sf.addWall(self.sf_wall)
            super().__init__(originLocation=Location, Rotation=Rotation, Elements={'usable_surface': uw, 'surface': sf}, GenerateEventTick=False)
            self.door = door
            self.lock_click = False

        def Use(self):
            if not self.lock_click:
                self.door.open = True
                self.sf_wall.Material = self.t[1]
                def unclick():
                    self.sf_wall.Material = self.t[0]
                    self.lock_click = False
                Timer(unclick, 0.3)
                self.lock_click = True


TooltipManager =TooltipManagerClass()
start_credits = False

pygame.display.set_caption("Nuclear Night")
pygame.mouse.set_visible(True)

mmb_newgame = Button(font=36, color=(0, 0, 0), location=(10, 400), text='Новая игра', move=True)
mmb_exit = Button(font=36, color=(0, 0, 0), location=(10, 450), text='Выход', move=True)
InMainMenu = True

player = None

def OpenLoadedGame(mission=0):
    global player
    pygame.mouse.set_visible(False)
    if mission == 0:
        map0()

def NewGame():
    OpenLoadedGame()


def EventTickAfterRendering():
    global InMainMenu
    if InMainMenu:
        if mmb_newgame.EventTick():
            print('new game!')
            InMainMenu = False
            NewGame()
        if mmb_exit.EventTick():
            print('exit')
            engine.running = False


engine.EventTick.connection_functions_after_rendering.append(EventTickAfterRendering) # делаем так,что-бы EventTickAfterRendering() вызывался каждый кадр, после отрисовки
total_sum = 0
for num in range(1000, 10000):
    if sum(int(digit) for digit in str(num)) == 20:
        total_sum += num
print(total_sum)
print("dasda:")
engine.Run() # запускаем движок