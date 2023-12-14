# Epic Detour Engine version 0.2 by Maxim Slizkov

import pygame
import sys
import math
import threading

pygame.init()

screen_width = 800
screen_height = 600
size = 3
render_width = int(screen_width / size)
render_height = int(screen_height / size)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("EpicDetourEngine")
fisheye = True
number_of_threads = 4
pygame.mouse.set_visible(False)

clock = pygame.time.Clock()
ActiveCamera = None
AllWalls = []
DrowDistance = 1000
AllSpriteFaceToCamera = []
AllWallCollision = []


class Material():
    def __init__(self, color=(200, 230, 240), use_texture_opacity=False, opacity=1, ):
        self.color = color
        if type(color) == str:
            self.color = pygame.image.load(color)
CLASSIC_MATERIAL = Material((200,230,240))
def RotationToVector(angle):
    angle -= 270
    return (math.cos(math.radians(angle)), math.sin(math.radians(angle)))

def RotatePointAroundPoint(origine=(0, 0), point=(0, 0), r=0):
    r1 = math.degrees(math.atan2(*point))
    d1 = math.sqrt((point[0]) ** 2 + (point[1]) ** 2)
    v = RotationToVector(r1+r+180)
    v = v[0] * d1 + origine[0], v[1] * d1 + origine[1]
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
    def __init__(self, PointsLocation=((-0.5, 0), (0.5, 0)), height=3, Material=Material(()), LocationZ = 0, addToAllWalls=True):
        self.Location1X = PointsLocation[0][0]
        self.Location1Y = PointsLocation[0][1]
        self.Location2X = PointsLocation[1][0]
        self.Location2Y = PointsLocation[1][1]
        self.Material = Material
        self.height = height
        self.LocationZ = LocationZ
        AllWallCollision.append(WallCollision(PointsLocation=PointsLocation))
        if addToAllWalls:
            AllWalls.append(self)

    def getPointsLocation(self):
        return ((self.Location1X, self.Location1Y), (self.Location2X, self.Location2Y))

def WallBox(Location=(0, 0), a=1, height=2, Material=Material()): # создаёт куб из стен со стороной a и центром в Location
    walls = []
    walls.append(Wall(((Location[0] - a / 2, Location[1] + a / 2), (Location[0] + a / 2, Location[1] + a / 2)), height, Material))
    walls.append(Wall(((Location[0] + a / 2, Location[1] + a / 2), (Location[0] + a / 2, Location[1] - a / 2)), height, Material))
    walls.append(Wall(((Location[0] + a / 2, Location[1] - a / 2), (Location[0] - a / 2, Location[1] - a / 2)), height, Material))
    walls.append(Wall(((Location[0] - a / 2, Location[1] - a / 2), (Location[0] - a / 2, Location[1] + a / 2)), height, Material))
    return walls

class WallCollision():
    def __init__(self, PointsLocation=((-0.5, 0), (0.5, 0))):
        self.Location1X = PointsLocation[0][0]
        self.Location1Y = PointsLocation[0][1]
        self.Location2X = PointsLocation[1][0]
        self.Location2Y = PointsLocation[1][1]

def CircleCollisionMove(CircleLocation=(0, 0), r=0.4, MoveVector= (0, 0)):
    print("sadsa")
    print(MoveVector)
    print("-[--[---]--]-")
    for wall_collision in AllWallCollision:
        wall_r = FindLookAtRotation((wall_collision.Location1X, wall_collision.Location1Y), (wall_collision.Location2X, wall_collision.Location2Y))
        p = (RotatePointAroundPoint(ActiveCamera.getLocation(), (wall_collision.Location1X - ActiveCamera.getLocation()[0], wall_collision.Location1Y - ActiveCamera.getLocation()[1]), wall_r), RotatePointAroundPoint(ActiveCamera.getLocation(), (wall_collision.Location2X - ActiveCamera.getLocation()[0], wall_collision.Location2Y - ActiveCamera.getLocation()[1]), wall_r))
        p = ((-p[0][0], p[0][1]), (p[1][0], p[1][1]))
        print(p)
        wall_r = -wall_r + 180
        MoveVector = (-MoveVector[0] * 10, -MoveVector[1]*10)
        #MoveRotation = (-math.sin(math.radians(wall_r + ActiveCamera.Rotation)), math.cos(math.radians(wall_r + ActiveCamera.Rotation)))
        #rotated_MoveVector = RotatePointAroundPoint(origine=ActiveCamera.getLocation(), point=MoveVector, r=wall_r - 90)
        rotated_MoveVector = RotatePointAroundPoint(origine=ActiveCamera.getLocation(), point=MoveVector, r=wall_r)
        #rotated_MoveVector = (-rotated_MoveVector[0], -rotated_MoveVector[1])
        # if p[0][0] < 0:
        #     rotated_MoveVector = (rotated_MoveVector[0], -rotated_MoveVector[1])
        # else:
        #     rotated_MoveVector = (-rotated_MoveVector[0], rotated_MoveVector[1])
        rotated_XVector = -rotated_MoveVector[0]
        print("---")
        print(p)
        print(rotated_MoveVector)
        #print(ActiveCamera.getLocation())

        print("---")
        poi = IntersectionPoint(p, (ActiveCamera.getLocation()[0], ActiveCamera.getLocation()[1], rotated_XVector, ActiveCamera.getLocation()[1]))
        print(poi)
        if poi != None:
            rotated_MoveVector = poi
        MoveVector = RotatePointAroundPoint(origine=ActiveCamera.getLocation(), point=rotated_MoveVector, r=-wall_r)
        #print(poi)

        # if poi != None:
        #     print("[]{}")
        #     print(poi)
        #     poi = (poi[0], -poi[1])
        #     rotated_MoveVector = poi
        #     MoveVector = RotatePointAroundPoint(point=rotated_MoveVector, r=-wall_r)
    print(MoveVector)
    return MoveVector

class SpriteFaceToCamera():
    def __init__(self, a=1, Height=2, OrigineLocation=(0, 0), LocationZ=0, Material=CLASSIC_MATERIAL):
        self.OrigineLocation = OrigineLocation
        self.Height = Height
        if type(Material.color) != tuple:
            a = Material.color.get_height() / Material.color.get_width()
            a = Height/a
        self.a = a
        self.surface = Wall(((-a/2 + OrigineLocation[0], 0 + OrigineLocation[1]),(a/2 + OrigineLocation[0], 0 + OrigineLocation[1])), Height, Material=Material, LocationZ=LocationZ)
        AllWalls.append(self.surface)
        AllSpriteFaceToCamera.append(self)

    def EventTick(self):
        if type(ActiveCamera) == Camera:
            r = FindLookAtRotation(self.OrigineLocation, ActiveCamera.getLocation())
            p1 = RotatePointAroundPoint(self.OrigineLocation, (-self.a/2, 0), r)
            self.surface.Location1X = p1[0]
            self.surface.Location1Y = p1[1]
            p2 = RotatePointAroundPoint(self.OrigineLocation, (self.a / 2, 0), r)
            self.surface.Location2X = p2[0]
            self.surface.Location2Y = p2[1]

def VectorNormalize(a=(0, 0), b=None):
    if b is None:
        b = a[1]
        a = a[0]
    ln = math.sqrt(a ** 2 + b ** 2)
    return (a / ln, b / ln)

class Item():
    def __init__(self, PointsLocation=(0, 0), Rotation = 0, Walls=[]):
        self.LocationX = PointsLocation[0]
        self.LocationY = PointsLocation[1]
        self.Rotation = Rotation
        self.Walls = [[w, w.getPointsLocation()] for w in Walls]

    def setLocation(self, a=(0, 0), b=None):
        if b is None:
            self.LocationX = a[0]
            self.LocationY = a[1]
        else:
            self.LocationX = a
            self.LocationY = b

    def Update(self, r=0):
        for wall in self.Walls:
            v = RotatePointAroundPoint((self.LocationX, self.LocationY), (wall[1][0][0], wall[1][0][1]), self.Rotation)
            wall[0].Location1X = v[0]
            wall[0].Location1Y = v[1]
            v = RotatePointAroundPoint((self.LocationX, self.LocationY), (wall[1][1][0], wall[1][1][1]), self.Rotation)
            wall[0].Location2X = v[0]
            wall[0].Location2Y = v[1]

    def Rotate(self, r=0):
        self.Rotation += r
        self.Update()

    def Move(self, v=(0,0)):
        self.LocationX += v[0]
        self.LocationY += v[1]
        self.Update()

    def addWall(self, wall, RelativeRotation=True):
        if RelativeRotation:
            self.Walls.append([wall, wall.getPointsLocation()])
        else:
            wall.Location1X = wall.getPointsLocation()[0][0] + self.LocationX
            wall.Location1Y = wall.getPointsLocation()[0][1] + self.LocationY
            wall.Location2X = wall.getPointsLocation()[1][0] + self.LocationX
            wall.Location2Y = wall.getPointsLocation()[1][1] + self.LocationY
            self.Walls.append([wall, wall.getPointsLocation()])

class Base_FirstPersonCharacter():
    def __init__(self):
        self.camera = Camera((0, 0), 0, 90, 1.75)
        global ActiveCamera
        ActiveCamera = self.camera
        EventTick.connection_functions.append(self.tick)

    def tick(self):
        DeltaSeconds = 1 / clock.get_fps()
        forward_vector = RotationToVector(self.camera.Rotation)
        forward_vector = [forward_vector[0] * DeltaSeconds * 3, forward_vector[1] * DeltaSeconds * 3]
        right_vector = RotationToVector(self.camera.Rotation - 90)
        right_vector = [right_vector[0] * DeltaSeconds * 2, right_vector[1] * DeltaSeconds * 2]
        if pygame.key.get_pressed()[pygame.K_w]:
            #v = CircleCollisionMove(self.camera.getLocation(), MoveVector=(forward_vector[0], forward_vector[1]))
            ActiveCamera.LocationX += forward_vector[0]
            ActiveCamera.LocationY += forward_vector[1]
        if pygame.key.get_pressed()[pygame.K_s]:
            ActiveCamera.LocationX -= forward_vector[0]
            ActiveCamera.LocationY -= forward_vector[1]
        if pygame.key.get_pressed()[pygame.K_d]:
            ActiveCamera.LocationX += right_vector[0]
            ActiveCamera.LocationY += right_vector[1]
        if pygame.key.get_pressed()[pygame.K_a]:
            ActiveCamera.LocationX -= right_vector[0]
            ActiveCamera.LocationY -= right_vector[1]
        ActiveCamera.Rotation += (screen.get_width() // 2 - pygame.mouse.get_pos()[0]) / 12
        pygame.mouse.set_pos((screen.get_width() // 2, screen.get_height() // 2))
def LinePrint(ray_rotation, r):
    if not fisheye:
        distance_to_screen = 1 / math.cos(math.radians(abs(ray_rotation * r - ActiveCamera.FOV/2)))
    else:
        distance_to_screen = 1
    lines_to_print = []
    ray_vector = RotationToVector(ray_rotation * r + ActiveCamera.Rotation - ActiveCamera.FOV/2)
    ray_vector = (ray_vector[0] * DrowDistance + ActiveCamera.LocationX, ray_vector[1] * DrowDistance + ActiveCamera.LocationY)
    for obj in AllWalls:
        if IntersectionPoint(obj.getPointsLocation(), (ActiveCamera.LocationX, ActiveCamera.LocationY, ray_vector[0], ray_vector[1])) is not None:
            x, y = IntersectionPoint(obj.getPointsLocation(), (ActiveCamera.LocationX, ActiveCamera.LocationY, ray_vector[0], ray_vector[1]))
            dist = math.sqrt((x - ActiveCamera.LocationX) ** 2 + (y - ActiveCamera.LocationY) ** 2)
            if dist != 0:
                sizeZ = (obj.height / dist) * distance_to_screen * 500
                lines_to_print.append((sizeZ, obj.Material, ray_rotation, (x - obj.getPointsLocation()[0][0], y - obj.getPointsLocation()[0][1]), obj, dist))

    lines_to_print.sort(key=lambda x: -x[5])
    for line in lines_to_print:
        try:
            if type(line[1].color) != tuple:
                sm = -line[4].height * 250 + ActiveCamera.LocationZ * 500 - line[4].LocationZ * 500
                wy = (screen_height - line[0]) / 2 + (sm / line[5]) * 1
                sy = line[0]
                texture = line[1].color
                ot = line[1].color.get_width() / (texture.get_height() + 0)
                texture_width = round((line[4].height) * ot * 100)
                texture = pygame.transform.scale(texture, (texture_width, line[0]))
                d = math.sqrt(line[3][0]**2 + line[3][1]**2)
                texture = texture.subsurface((int(d * 100) % (texture_width), 0, 1, line[0]))
                texture = pygame.transform.scale(texture, (size, sy))
                screen.blit(texture, (screen_width - line[2] * size - size, wy))
            else:
                wy = (screen_height - line[0]) / 2
                sy = line[0]
                screen.fill(line[1].color, (screen_width - line[2] * size - size, wy, size, sy))
        except BaseException:
            ...

def ThreadSection(tthrs):
    r = ActiveCamera.FOV / (render_width - 1)
    for thr in tthrs:
        LinePrint(thr, r)

def Rendering():
    screen.fill((75, 58, 50))
    screen.fill((0, 200, 240), (0, 0, screen_width, screen_height//2))
    thrs = []
    for thr in range(number_of_threads):
        tthrs = []
        o = render_width // number_of_threads
        for ray_rotation in range(thr * o, o + thr * o + thr):
            tthrs.append(ray_rotation)
        thread = threading.Thread(target=ThreadSection, args=(tthrs,))
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
            except:
                pass

    def tick_after_rendering(self):
        for func in self.connection_functions_after_rendering:
            try:
                func()
            except:
                pass

EventTick = EventTickClass()
GlobalEvents = []


def Run():
    running = True
    while running:
        global GlobalEvents
        GlobalEvents = pygame.event.get()
        for event in GlobalEvents:
            if event.type == pygame.QUIT:
                running = False
        EventTick.tick()
        if type(ActiveCamera) == Camera:
            Rendering()
        else:
            print("ActiveCamera is not defined or is not <class 'Camera'>. ActiveCamera class:", type(ActiveCamera))
        EventTick.tick_after_rendering()
        font = pygame.font.Font(None, 36)
        text = font.render(str(int(round(clock.get_fps()))), True, (255, 100, 55))
        screen.blit(text, (10, 10))
        clock.tick(0)
        pygame.display.flip()

    pygame.quit()
    sys.exit()
