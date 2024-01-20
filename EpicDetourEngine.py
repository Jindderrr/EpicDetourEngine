# Epic Detour Engine version 0.4.1 by Maxim Slizkov

import pygame
import sys
import math
import threading
import time

pygame.init()


screen_width = 800
screen_height = 600
size = 2

FullScreen = False
if FullScreen:
    screen = pygame.display.set_mode((0, 0), FullScreen)
    screen_width = screen.get_width()
    screen_height = screen.get_height()
else:
    screen = pygame.display.set_mode((screen_width, screen_height))
render_width = int(screen_width / size)
render_height = int(screen_height / size)
pygame.display.set_caption("EpicDetourEngine")
fisheye = True
number_of_threads = 4
pygame.mouse.set_visible(False)
NumOfWallsForRender = 0
CuttingOffWallsOutsideFOV = True
WorldDeltaSeconds = 0
clock = pygame.time.Clock()
ActiveCamera = None
AllWalls = []
DrowDistance = 1000
AllSpriteFaceToCamera = []
AllWallCollision = []
ResizeZTexture = False
MinFPS = 15
max_size = 8
min_size = 1
auto_size = True
texture_onecolor_dist = 20
AllTrackers = []
TextureQuality = 1
NumActors = 0

class Material():
    def __init__(self, color=(200, 230, 240), use_onecolor_texture=True, use_texture_opacity=False, opacity=1, ):
        self.color = color
        if type(color) == str:
            self.color = pygame.image.load(color)
            if use_onecolor_texture:
                pixels = pygame.image.tostring(self.color, 'RGB')
                r, g, b, o = (0, 0, 0, 0)
                for pixel in pixels:
                    if o == 0:
                        r += pixel
                    elif o == 1:
                        g += pixel
                    elif o == 2:
                        b += pixel
                    o += 1
                    if o == 3:
                        o = 0
                np = self.color.get_size()[0] * self.color.get_size()[1]
                r = round(r / np)
                g = round(g / np)
                b = round(b / np)
                self.onecolor = (r, g, b)
            if TextureQuality != 1:
                self.color = pygame.transform.scale(self.color, (self.color.get_width() // TextureQuality, self.color.get_height() // TextureQuality))

CLASSIC_MATERIAL = Material((200,230,240))
def RotationToVector(angle):
    angle -= 270
    return (math.cos(math.radians(angle)), math.sin(math.radians(angle)))

def NormalizeRotation(rotation):
    return rotation % 360

def RotatePointAroundPoint(origin=(0, 0), point=(0, 0), r=0):
    r1 = math.degrees(math.atan2(*point))
    d1 = math.sqrt((point[0]) ** 2 + (point[1]) ** 2)
    v = RotationToVector(r1+r+180)
    v = v[0] * d1 + origin[0], v[1] * d1 + origin[1]
    return v[0], v[1]

def FindLookAtRotation(Start, Target):
    return -math.degrees(math.atan2(Start[1] - Target[1], Target[0] - Start[0])) + 90

class Camera():
    def __init__(self, Location=(0, 0), Rotation=0, FOV = 90, LocationZ= 0):
        self.LocationX = Location[0]
        self.LocationY = Location[1]
        self.Rotation = Rotation
        self.FOV = FOV
        self.LocationZ = LocationZ

    def getLocation(self):
        return (self.LocationX, self.LocationY)

    def setLocation(self, a=(0, 0), b=None):
        if b is None:
            self.LocationX = a[0]
            self.LocationY = a[1]
        else:
            self.LocationX = a
            self.LocationY = b

class Wall():
    def __init__(self, PointsLocation=((-0.5, 0), (0.5, 0)), height=3, Material=CLASSIC_MATERIAL, LocationZ = 0, addToAllWalls=True, collision=True):
        self.Location1X = PointsLocation[0][0]
        self.Location1Y = PointsLocation[0][1]
        self.Location2X = PointsLocation[1][0]
        self.Location2Y = PointsLocation[1][1]
        self.Material = Material
        self.height = height
        self.LocationZ = LocationZ
        if collision:
            AllWallCollision.append(WallCollision(PointsLocation=PointsLocation))
        if addToAllWalls:
            AllWalls.append(self)

    def getPointsLocation(self):
        return ((self.Location1X, self.Location1Y), (self.Location2X, self.Location2Y))

    def RotateAroundPoint(self, point):
            v = RotatePointAroundPoint(point.getLocation(), self.getPointsLocation(), self.Rotation)
            self.Location1X = v[0]
            self.Location1Y = v[1]
            v = RotatePointAroundPoint(point.getLocation(), self.getPointsLocation(), self.Rotation)
            self.Location2X = v[0]
            self.Location2Y = v[1]

def WallBox(Location=(0, 0), height=2, a=1, Material=Material()): # создаёт куб из стен со стороной a и центром в Location
    walls = []
    walls.append(Wall(((Location[0] - a / 2, Location[1] + a / 2), (Location[0] + a / 2, Location[1] + a / 2)), height, Material))
    walls.append(Wall(((Location[0] + a / 2, Location[1] + a / 2), (Location[0] + a / 2, Location[1] - a / 2)), height, Material))
    walls.append(Wall(((Location[0] + a / 2, Location[1] - a / 2), (Location[0] - a / 2, Location[1] - a / 2)), height, Material))
    walls.append(Wall(((Location[0] - a / 2, Location[1] - a / 2), (Location[0] - a / 2, Location[1] + a / 2)), height, Material))
    return walls

class WallCollision():
    def __init__(self, PointsLocation=((-0.5, 0), (0.5, 0)), Type="NoType"):
        self.Location1X = PointsLocation[0][0]
        self.Location1Y = PointsLocation[0][1]
        self.Location2X = PointsLocation[1][0]
        self.Location2Y = PointsLocation[1][1]
        self.Type = Type

    def getPointsLocation(self):
        return ((self.Location1X,self.Location1Y), (self.Location2X, self.Location2Y))

def getWallCollisionByTypes(Types=('NoType')):
    return [cw for cw in AllWallCollision if cw.Type in Types]

def CircleCollisionMove(CircleLocation=(0, 0), MoveVector= (0, 0), r=0.4, CollisionWalls=AllWallCollision):
    for wall_collision in CollisionWalls:
        wall_r = FindLookAtRotation((wall_collision.Location1X, wall_collision.Location1Y), (wall_collision.Location2X, wall_collision.Location2Y))
        p = ((wall_collision.Location1X - CircleLocation[0], wall_collision.Location1Y - CircleLocation[1]), (wall_collision.Location2X - CircleLocation[0], wall_collision.Location2Y - CircleLocation[1]))
        p = (RotatePointAroundPoint((0, 0), p[0], wall_r), RotatePointAroundPoint((0, 0), p[1], wall_r))
        p = ((p[0][0], -p[0][1]), (p[1][0], -p[1][1]))
        wall_r = NormalizeRotation(-wall_r)
        mv = RotatePointAroundPoint((0, 0), MoveVector, -wall_r)
        mv = [mv[0], mv[1]]
        x = mv[0]
        y = mv[1]
        if p[0][0] > 0:
            x += r
        else:
            x -= r
        if (p[0][1] < 0 < p[1][1] or p[0][1] > 0 > p[1][1]):
        #if (abs((p[0][1] - p[1][1])) + abs(y) >= (abs(max((p[0][1], p[1][1], y + r)) - min((p[0][1], p[1][1], y - r))))):
            if x > p[0][0] > 0 or x < p[0][0] < 0:
                print(time.monotonic())
                x = p[0][0]
                mv = [x, y]
                if x > 0:
                    mv[0] -= r
                else:
                    mv[0] += r
                mv = RotatePointAroundPoint((0, 0), mv, -wall_r)
                MoveVector = mv
                MoveVector = (MoveVector[0], MoveVector[1])
    return [MoveVector[0], MoveVector[1]]

class SpriteFaceToCamera():
    def __init__(self, a=1, Height=2, OriginLocation=(0, 0), LocationZ=0, Material=CLASSIC_MATERIAL, collision=False, collisionType='NoType'):
        self.LocationX = OriginLocation[0]
        self.LocationY = OriginLocation[1]
        self.Height = Height
        if type(Material.color) != tuple:
            a = Material.color.get_height() / Material.color.get_width()
            a = Height/a
        self.a = a
        self.surface = Wall(((-a/2 + OriginLocation[0], 0 + OriginLocation[1]), (a/2 + OriginLocation[0], 0 + OriginLocation[1])), Height, Material=Material, LocationZ=LocationZ, collision=False)
        self.c_surface = None
        if collision:
            self.c_surface = WallCollision(((-a/2 + OriginLocation[0], 0 + OriginLocation[1]), (a/2 + OriginLocation[0], 0 + OriginLocation[1])), collisionType)
            AllWallCollision.append(self.c_surface)
        AllSpriteFaceToCamera.append(self)
        self.LocationZ = LocationZ

    def EventTick(self):
        if type(ActiveCamera) == Camera:
            OriginLocation = (self.LocationX, self.LocationY)
            r = FindLookAtRotation(OriginLocation, ActiveCamera.getLocation())
            p1 = RotatePointAroundPoint(OriginLocation, (-self.a / 2, 0), r)
            self.surface.Location1X = p1[0]
            self.surface.Location1Y = p1[1]
            p2 = RotatePointAroundPoint(OriginLocation, (self.a / 2, 0), r)
            self.surface.Location2X = p2[0]
            self.surface.Location2Y = p2[1]
            if self.c_surface != None:
                p1 = RotatePointAroundPoint(OriginLocation, (-self.a / 2, 0), r)
                self.c_surface.Location1X = p1[0]
                self.c_surface.Location1Y = p1[1]
                p2 = RotatePointAroundPoint(OriginLocation, (self.a / 2, 0), r)
                self.c_surface.Location2X = p2[0]
                self.c_surface.Location2Y = p2[1]

def VectorNormalize(a=(0, 0), b=None):
    if b is None:
        b = a[1]
        a = a[0]
    ln = math.sqrt(a ** 2 + b ** 2)
    return (a / ln, b / ln)

class Item():
    def __init__(self, OriginLocation=(0, 0), LocationZ=0, Rotation=0, Walls=[], collision=True):
        self.LocationX = OriginLocation[0]
        self.LocationY = OriginLocation[1]
        self.LocationZ = LocationZ
        self.Rotation = Rotation
        self.Walls = [[w, w.getPointsLocation(), w.LocationZ] for w in Walls]
        if collision:
            self.c_Walls = [[w, w.getPointsLocation(), w.LocationZ] for w in Walls]

    def setLocation(self, a=(0, 0), b=None):
        if b is None:
            self.LocationX = a[0]
            self.LocationY = a[1]
        else:
            self.LocationX = a
            self.LocationY = b

    def Update(self):
        for wall in self.Walls + self.c_Walls:
            v = RotatePointAroundPoint((self.LocationX, self.LocationY), (wall[1][0][0], wall[1][0][1]), self.Rotation)
            wall[0].Location1X = v[0]
            wall[0].Location1Y = v[1]
            v = RotatePointAroundPoint((self.LocationX, self.LocationY), (wall[1][1][0], wall[1][1][1]), self.Rotation)
            wall[0].Location2X = v[0]
            wall[0].Location2Y = v[1]
            wall[0].LocationZ = self.LocationZ + wall[2]


    def Rotate(self, r=0):
        self.Rotation += r
        self.Update()

    def Move(self, v=(0,0)):
        self.LocationX += v[0]
        self.LocationY += v[1]
        self.Update()

    def addWall(self, wall, RelativeRotation=True, collision=True):
        if RelativeRotation:
            self.Walls.append([wall, wall.getPointsLocation(), wall.LocationZ])
            if collision:
                cw = WallCollision(wall.getPointsLocation())
                AllWallCollision.append(cw)
                self.c_Walls.append([cw, wall.getPointsLocation(), wall.LocationZ])
        else:
            wall.Location1X = wall.getPointsLocation()[0][0] + self.LocationX
            wall.Location1Y = wall.getPointsLocation()[0][1] + self.LocationY
            wall.Location2X = wall.getPointsLocation()[1][0] + self.LocationX
            wall.Location2Y = wall.getPointsLocation()[1][1] + self.LocationY
            self.Walls.append([wall, wall.getPointsLocation(), wall.LocationZ])
            cw = WallCollision(wall.getPointsLocation())
            cw.Location1X = wall.getPointsLocation()[0][0] + self.LocationX
            cw.Location1Y = wall.getPointsLocation()[0][1] + self.LocationY
            cw.Location2X = wall.getPointsLocation()[1][0] + self.LocationX
            cw.Location2Y = wall.getPointsLocation()[1][1] + self.LocationY
            self.c_Walls.append([cw, wall.getPointsLocation(), wall.LocationZ])

def OpenOBJAsMap(file_path, materials={}):
    with open(file_path) as file:
        rs = []
        current_item = None
        vertices = []
        for string in file.read().split("\n"):
            if string != "":
                if string[0] == "o":
                    current_item = [Item(), string.split()[1]]
                elif current_item != None:
                    pn = current_item[1].split("_")
                    if string[0] == "v":
                        vertices.append((float(string.split()[1]), -float(string.split()[3])))
                        if pn[0] == 'wallbox':
                            current_item.append(WallBox((float(string.split()[1]), -float(string.split()[3])), float(pn[1]), float(pn[2]), materials[pn[3]]))
                        elif pn[0] == 'sprite':
                            current_item.append(SpriteFaceToCamera(a=float(pn[1]), Height=float(pn[2]), OriginLocation=(float(string.split()[1]), -float(string.split()[3])), LocationZ=float(pn[3]), Material=materials[pn[4]]))
                        else:
                            rs.append((pn, (float(string.split()[1]), -float(string.split()[3]))))
                    elif string[0] == "l":
                        if pn[0] == 'wall':
                            current_item.append(Wall(PointsLocation=((vertices[int(string.split()[1]) - 1][0], vertices[int(string.split()[1]) - 1][1]), (vertices[int(string.split()[2]) - 1][0], vertices[int(string.split()[2]) - 1][1])), height=float(pn[1]), Material=materials[pn[2]], LocationZ=float(pn[3]), addToAllWalls=float(pn[4])))
    return rs

class Actor():
    def __init__(self, originLocation=(0, 0), LocationZ=0, Rotation=0, Elements={}, GenerateEventTick=True, GenerateEventTickAfterRendering=False):
        self.LocationX = originLocation[0]
        self.LocationY = originLocation[1]
        self.LocationZ = LocationZ
        self.Rotation = Rotation
        self.AllElements = {}
        self.add(Elements)
        if GenerateEventTick:
            try:
                EventTick.connection_functions.append(self.EventTick)
            except BaseException as e:
                print(e)
        if GenerateEventTickAfterRendering:
            try:
                EventTick.connection_functions_after_rendering.append(self.EventTickAfterRendering)
            except BaseException as e:
                print(e)
        global NumActors
        NumActors += 1
        self.add(Elements)

    def add(self, Elements):
        r_elems = []
        for elem in Elements:
            if type(Elements[elem]) in (Item, Camera):
                self.AllElements[elem] = [Elements[elem], (Elements[elem].LocationX, Elements[elem].LocationY, Elements[elem].LocationZ, Elements[elem].Rotation)]
            elif type(Elements[elem]) == InBoxDetector:
                self.AllElements[elem] = [Elements[elem], (Elements[elem].LocationX, Elements[elem].LocationY, Elements[elem].Rotation)]
            elif type(Elements[elem]) == SpriteFaceToCamera:
                self.AllElements[elem] = [Elements[elem], (Elements[elem].LocationX, Elements[elem].LocationY, Elements[elem].LocationZ)]
            elif type(Elements[elem]) == Tracker:
                self.AllElements[elem] = [Elements[elem], (Elements[elem].LocationX, Elements[elem].LocationY)]
            else: r_elems.append(elem)
        self.Update()
        return r_elems

    def getLocation(self):
        return self.LocationX, self.LocationY

    def setLocation(self, a=(0, 0), b=None):
        if b is None:
            self.LocationX = a[0]
            self.LocationY = a[1]
        else:
            self.LocationX = a
            self.LocationY = b

    def setElementLocalLocation(self, name, Location = (0, 0)):
        if type(self.AllElements[name][0]) in (Item, Camera):
            self.AllElements[name][1] = (Location[0], Location[1], self.AllElements[name][1][2], self.AllElements[name][1][3])
        elif type(self.AllElements[name][0]) in (InBoxDetector, SpriteFaceToCamera):
            self.AllElements[name][1] = (Location[0], Location[1], self.AllElements[name][1][2])
        elif type(self.AllElements[name][0]) == Tracker:
            self.AllElements[name][1] = (Location[0], Location[1])
        else:
            return 'sam davay'
        self.Update()

    def Move(self, v=(0,0)):
        self.LocationX += v[0]
        self.LocationY += v[1]
        self.Update()

    def Rotate(self, r=0):
        self.Rotation += r
        self.Update()

    def getElem(self, name):
        return self.AllElements[name]

    def Update(self):
        r_elems = []
        for elem in self.AllElements:
            elemRef = self.AllElements[elem][0]
            elemX, elemY = RotatePointAroundPoint(self.getLocation(), (self.AllElements[elem][1][0], self.AllElements[elem][1][1]), self.Rotation)
            if type(elemRef) in (Item, Camera):
                elemRef.LocationX = elemX
                elemRef.LocationY = elemY
                elemRef.LocationZ = self.AllElements[elem][1][2] + self.LocationZ
                elemRef.Rotation = self.Rotation
                if type(elemRef) == Item:
                    elemRef.Update()
            elif type(elemRef) == InBoxDetector:
                elemRef.LocationX = elemX
                elemRef.LocationY = elemY
                elemRef.Rotation = self.Rotation
            elif type(elemRef) == SpriteFaceToCamera:
                elemRef.LocationX = elemX
                elemRef.LocationY = elemY
                elemRef.LocationZ = self.AllElements[elem][1][2] + self.LocationZ
            elif type(self.AllElements[elem][0]) == Tracker:
                elemRef.LocationX = elemX
                elemRef.LocationY = elemY
            else: r_elems.append(elem)
        return r_elems

    def Destroy(self):
        for eln in self.AllElements:
            elr = self.AllElements[eln][0]
            if type(elr) == SpriteFaceToCamera:
                AllSpriteFaceToCamera.pop(AllSpriteFaceToCamera.index(elr))
                for n, wall in enumerate(AllWalls):
                    if wall == elr.surface:
                        AllWalls.pop(n)
                        break
            try:
                EventTick.connection_functions.pop(EventTick.connection_functions.index(self.EventTick))
            except:
                ...
        global NumActors
        NumActors -= 1

class Tracker():
    def __init__(self, Tags=[]):
        self.Tags = Tags
        self.LocationX = 0
        self.LocationY = 0
        AllTrackers.append(self)

class InBoxDetector():
    def __init__(self, Location=(0, 0), size=(1, 1), Rotation=0):
        self.LocationX = Location[0]
        self.LocationY = Location[1]
        self.size = size
        self.Rotation = Rotation

    def AllInBox(self):
        all_in = []
        for tracker in AllTrackers:
            rotated_point = RotatePointAroundPoint((self.LocationX, self.LocationY), (tracker.LocationX - self.LocationX, -tracker.LocationY + self.LocationY), -self.Rotation)
            if self.LocationX - self.size[0] / 2 <= rotated_point[0] <= self.LocationX + self.size[0] / 2 and self.LocationY - self.size[1] / 2 <= rotated_point[1] <= self.LocationY + self.size[1] / 2:
                all_in.append(tracker)
        return all_in

class Base():
    class Character(Actor):
        def __init__(self, originLocation=(0, 0), GenerateEventTickAfterRendering=False, CollisionWith=('NoType')):
            super().__init__(originLocation=originLocation, GenerateEventTickAfterRendering=GenerateEventTickAfterRendering)
            self.RightMove = 0
            self.ForwardMove = 0
            self.MoveVector = [0, 0]
            self.CollisionWith = CollisionWith

        def EventTick(self):
            cs = 30
            self.MoveVector = [self.MoveVector[0] * WorldDeltaSeconds, self.MoveVector[1] * WorldDeltaSeconds]
            self.MoveVector = CircleCollisionMove(CircleLocation=self.getLocation(), MoveVector=(self.MoveVector[0], self.MoveVector[1]), CollisionWalls=getWallCollisionByTypes(self.CollisionWith))
            self.MoveVector = [self.MoveVector[0] / WorldDeltaSeconds, self.MoveVector[1] / WorldDeltaSeconds]
            self.LocationX += self.MoveVector[0] * WorldDeltaSeconds
            self.LocationY += self.MoveVector[1] * WorldDeltaSeconds
            for n in range(2):
                if self.MoveVector[n] > 0:
                    self.MoveVector[n] -= WorldDeltaSeconds * cs
                    if self.MoveVector[n] < 0:
                        self.MoveVector[n] = 0
                elif self.MoveVector[n] < 0:
                    self.MoveVector[n] += WorldDeltaSeconds * cs
                    if self.MoveVector[n] > 0:
                        self.MoveVector[n] = 0
            self.Update()

    class FirstPersonCharacter(Character):
        def __init__(self):
            self.camera = Camera((0, 0), 0, 90, 1.65)
            global ActiveCamera
            ActiveCamera = self.camera
            super().__init__(GenerateEventTickAfterRendering=True)
            self.add({'camera': self.camera})
            self.EnableInput = True

        def EventTick(self):
            m = int(pygame.key.get_pressed()[pygame.K_LSHIFT]) * 0.6 + 1
            fs = 4 * m
            rs = 3 * m
            forward_vector = RotationToVector(self.camera.Rotation)
            forward_vector = [forward_vector[0] * fs, forward_vector[1] * fs]
            right_vector = RotationToVector(self.camera.Rotation - 90)
            right_vector = [right_vector[0] * rs, right_vector[1] * rs]
            if self.EnableInput:
                if pygame.key.get_pressed()[pygame.K_w]:
                    self.MoveVector = [forward_vector[0], forward_vector[1]]
                if pygame.key.get_pressed()[pygame.K_s]:
                    self.MoveVector = [-forward_vector[0], -forward_vector[1]]
                if pygame.key.get_pressed()[pygame.K_d]:
                    self.MoveVector = [right_vector[0], right_vector[1]]
                if pygame.key.get_pressed()[pygame.K_a]:
                    self.MoveVector = [-right_vector[0], -right_vector[1]]
                self.Rotation += (screen.get_width() // 2 - pygame.mouse.get_pos()[0]) / 12
                pygame.mouse.set_pos((screen.get_width() // 2, screen.get_height() // 2))
            super().EventTick()

def LinePrint(ray_rotation, r, walls_for_render=None):
    if not fisheye:
        distance_to_screen = 1 / math.cos(math.radians(abs(ray_rotation * r - ActiveCamera.FOV/2)))
    else:
        distance_to_screen = 1
    lines_to_print = []
    ray_vector = RotationToVector(ray_rotation * r + ActiveCamera.Rotation - ActiveCamera.FOV/2)
    ray_vector = (ray_vector[0] * DrowDistance + ActiveCamera.LocationX, ray_vector[1] * DrowDistance + ActiveCamera.LocationY)
    if walls_for_render == None:
        walls_for_render = AllWalls
    for obj in walls_for_render:
        if IntersectionPoint(obj.getPointsLocation(), (ActiveCamera.LocationX, ActiveCamera.LocationY, ray_vector[0], ray_vector[1])) is not None:
            x, y = IntersectionPoint(obj.getPointsLocation(), (ActiveCamera.LocationX, ActiveCamera.LocationY, ray_vector[0], ray_vector[1]))
            dist = math.sqrt((x - ActiveCamera.LocationX) ** 2 + (y - ActiveCamera.LocationY) ** 2)
            if dist != 0:
                sizeZ = (obj.height / dist) * distance_to_screen * 0.66 * screen_width / (ActiveCamera.FOV/90)
                lines_to_print.append((sizeZ, obj.Material, ray_rotation, (x - obj.getPointsLocation()[0][0], y - obj.getPointsLocation()[0][1]), obj, dist))

    lines_to_print.sort(key=lambda x: -x[5])
    for line in lines_to_print:
        try:
            sm = -line[4].height * 250 + ActiveCamera.LocationZ * 500 - line[4].LocationZ * 500
            if ResizeZTexture:
                wy = round(((screen_height - line[0]) / 2 + (sm / line[5]) * 1) / size) * size
            else:
                wy = (screen_height - line[0]) / 2 + (sm / line[5]) * 1
            sy = line[0]
            texture = line[1].color
            if line[5] > texture_onecolor_dist and type(line[1].color) != tuple:
                texture = line[1].onecolor
            if type(texture) != tuple:
                ot = texture.get_width() / (texture.get_height() + 0)
                texture_width = round((line[4].height) * ot * 100)
                texture = pygame.transform.scale(texture, (texture_width, sy))
                d = math.sqrt(line[3][0]**2 + line[3][1]**2)
                texture = texture.subsurface((int(d * 100) % (texture_width), 0, 1, sy))
                if ResizeZTexture:
                    texture = pygame.transform.scale(texture, (size, sy/size))
                texture = pygame.transform.scale(texture, (size, sy))
                screen.blit(texture, (screen_width - line[2] * size - size, wy))
            else:
                sy = line[0]
                screen.fill(texture, (screen_width - line[2] * size - size, wy, size, sy))
        except BaseException:
            ...

def ThreadSection(tthrs, walls_for_render):
    r = ActiveCamera.FOV / (render_width - 1)
    for thr in tthrs:
        LinePrint(thr, r, walls_for_render)

def CheackWallsForRender():
    global NumOfWallsForRender
    if not CuttingOffWallsOutsideFOV:
        NumOfWallsForRender = len(AllWalls)
        return AllWalls
    c_FOV = ActiveCamera.FOV
    c_R = NormalizeRotation(ActiveCamera.Rotation)
    r_walls = []
    for wall in AllWalls:
        r1 = NormalizeRotation(FindLookAtRotation(ActiveCamera.getLocation(), wall.getPointsLocation()[0]) - 180)
        r2 = NormalizeRotation(FindLookAtRotation(ActiveCamera.getLocation(), wall.getPointsLocation()[1]) - 180)
        f1, f2 = NormalizeRotation(c_R - c_FOV / 2), NormalizeRotation(c_R + c_FOV / 2)
        if f2 > r1 > f1 or f2 > r2 > f1:
            r_walls.append(wall)
        elif (abs(c_R) < c_FOV / 2 or abs(c_R - 360) < c_FOV / 2) and ((f1 > r1 < f2) or (f1 > r2 < f2) or (f1 < r1 > f2) or (f1 < r2 > f2)):
            r_walls.append(wall)
        elif IntersectionPoint(wall.getPointsLocation(), (*ActiveCamera.getLocation(), ActiveCamera.LocationX + RotationToVector(c_R)[0] * DrowDistance, ActiveCamera.LocationY + RotationToVector(c_R)[1] * DrowDistance)) != None:
            r_walls.append(wall)
    NumOfWallsForRender = len(r_walls)
    return r_walls

def Rendering():
    screen.fill((65, 58, 50))
    screen.fill((70, 77, 65), (0, 0, screen_width, screen_height//2))
    thrs = []
    walls_for_render = CheackWallsForRender()
    for thr in range(number_of_threads):
        tthrs = []
        o = render_width // number_of_threads
        for ray_rotation in range(thr * o, o + thr * o + thr):
            tthrs.append(ray_rotation)
        thread = threading.Thread(target=ThreadSection, args=(tthrs, walls_for_render))
        thrs.append(thread)
        thread.start()
    for thread in thrs:
        thread.join()

def IntersectionPoint(line_segment, ray):
    x1, y1, x2, y2 = line_segment[0] + line_segment[1]
    x3, y3, x4, y4 = ray
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if d != 0:
        t1 = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
        if 0 <= t1 <= 1 and 0 <= -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / d <= 1:
            x = x1 + (x2 - x1) * t1
            y = y1 + (y2 - y1) * t1
            return (x, y)

def LineTrace(StartLocation, EndLocation, collide_walls=AllWalls):
    walls = []
    for wall_collision in collide_walls:
        p = IntersectionPoint(wall_collision.getPointsLocation(), (*StartLocation, *EndLocation))
        if p != None:
            walls.append((wall_collision, p))
    walls.sort(key=lambda x: ((((x[1][0] - StartLocation[0]) ** 2) + ((x[1][1] - StartLocation[1]) ** 2)) ** 0.5))
    return walls

class EventTickClass:
    def __init__(self):
        self.connection_functions = []
        self.connection_functions_after_rendering = []

    def tick(self):
        for S in AllSpriteFaceToCamera:
            S.EventTick()
        for func in self.connection_functions:
            try:
                func()
            except BaseException as e:
                print(e)

    def tick_after_rendering(self):
        for func in self.connection_functions_after_rendering:
            try:
                func()
            except BaseException as e:
                print(e)

EventTick = EventTickClass()
GlobalEvents = []
running = True


def Run():
    TypeOfStatistics = 0
    global running
    while running:
        global WorldDeltaSeconds, GlobalEvents, render_width, render_height, size
        LastFrame = time.monotonic()
        if auto_size:
            if WorldDeltaSeconds == 0: WorldDeltaSeconds = 0.001
            if WorldDeltaSeconds != 0:
                if 1 / WorldDeltaSeconds < MinFPS and size < max_size: size += 1
                if 1 / WorldDeltaSeconds > MinFPS * 2.3 and size != 1 and size > min_size: size -= 1
                render_width = int(screen_width / size)
                render_height = int(screen_height / size)
        GlobalEvents = pygame.event.get()
        for event in GlobalEvents:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKQUOTE:
                    TypeOfStatistics += 1
                    if TypeOfStatistics > 2: TypeOfStatistics = 0
        EventTick.tick()
        if type(ActiveCamera) == Camera:
            rt = time.monotonic()
            Rendering()
            rt = time.monotonic() - rt
        else:
            print("ActiveCamera is not defined or is not <class 'Camera'>. ActiveCamera class:", type(ActiveCamera))
            rt = 0
            screen.fill("white")
        EventTick.tick_after_rendering()
        if TypeOfStatistics == 1:
            font = pygame.font.Font(None, 36)
            color_value = int(round(clock.get_fps())) - 10
            if color_value < 0: color_value = 0
            if color_value > 50: color_value = 50
            if color_value != 0: color_value = (510 / 50) * color_value
            color_value = round(color_value)
            g = color_value
            r = 255
            if g > 255:
                g = 255
                r = 255 - (color_value - 255)
            text = font.render(str(int(round(clock.get_fps()))), True, (r, g, 0))
            screen.blit(text, (10, 10))
        if TypeOfStatistics == 2:
            font = pygame.font.Font(None, 20)
            texts = [f'FPS: {round(1 / WorldDeltaSeconds)}',
                     #f'Walls and Sprites: {len(AllWalls)}',
                     f'Walls: {len(AllWalls) - len(AllSpriteFaceToCamera)}',
                     f'Sprites: {len(AllSpriteFaceToCamera)}',
                     f'Walls and Sprites for render: {NumOfWallsForRender}',
                     f'Render width: {render_width}/{screen_width} ({size})',
                     f'Render time: {int(rt * 1000)}ms',
                     f'EventTick: {len(EventTick.connection_functions)}, after rendering: {len(EventTick.connection_functions_after_rendering)}',
                     f'Actors: {NumActors}']
            for y, text in enumerate(texts):
                screen.blit(font.render(text, True, (200, 230, 240)), (10, (y*18) + 8))
        pygame.display.flip()
        WorldDeltaSeconds = (time.monotonic() - LastFrame)
        clock.tick()

    pygame.quit()
    sys.exit()
