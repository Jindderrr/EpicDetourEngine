import pygame
import sys
import math

pygame.init()

screen_width = 720
screen_height = 405
size = 1
render_width = int(screen_width / size)
render_height = int(screen_height / size)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("EpicDetourEngine")
fisheye = False

clock = pygame.time.Clock()
ActiveCamera = None

def RotationToVector(angle):
    angle -= 270
    angle_rad = math.radians(angle)
    return (math.cos(math.radians(angle)), math.sin(math.radians(angle)))

def RotatePointAroundPoint(origine=(0, 0), point=(0, 0), r=0):
    point = (point[0], point[1])
    r1 = math.degrees(math.atan2(*point))
    d1 = math.sqrt((point[0]) ** 2 + (point[1]) ** 2)
    v = RotationToVector(r1+r+180)
    v = v[0] * d1 + origine[0], v[1] * d1 + origine[1]
    return v[0], v[1]

class Camera():
    def __init__(self, Location=(0, 0), Rotation=0, FOV = 90):
        self.LocationX = Location[0]
        self.LocationY = Location[1]
        self.Rotation = Rotation
        self.FOV = FOV

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
    def __init__(self, PointsLocation=((-0.5, 0), (0.5, 0)), Color=(200, 230, 240)):
        self.Location1X = PointsLocation[0][0]
        self.Location1Y = PointsLocation[0][1]
        self.Location2X = PointsLocation[1][0]
        self.Location2Y = PointsLocation[1][1]
        self.Color = Color

    def getPointsLocation(self):
        return ((self.Location1X, self.Location1Y), (self.Location2X, self.Location2Y))

def WallBox(Location=(0, 0), a=1, color=(0, 0, 0)): # создаёт куб из стен со стороной a и центром в Location
    walls = []
    walls.append(Wall(((Location[0] - a / 2, Location[1] + a / 2), (Location[0] + a / 2, Location[1] + a / 2)), color))
    walls.append(Wall(((Location[0] + a / 2, Location[1] + a / 2), (Location[0] + a / 2, Location[1] - a / 2)), color))
    walls.append(Wall(((Location[0] + a / 2, Location[1] - a / 2), (Location[0] - a / 2, Location[1] - a / 2)), color))
    walls.append(Wall(((Location[0] - a / 2, Location[1] - a / 2), (Location[0] - a / 2, Location[1] + a / 2)), color))
    return walls

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
        self.camera = Camera((0, 0), 0, 90)
        global ActiveCamera
        ActiveCamera = self.camera
        EventTick.connection_functions.append(self.tick)

    def tick(self):
        DeltaSeconds = 1 / clock.get_fps()
        forward_vector = RotationToVector(self.camera.Rotation)
        forward_vector = [forward_vector[0] * DeltaSeconds * 2, forward_vector[1] * DeltaSeconds * 2]
        right_vector = RotationToVector(self.camera.Rotation - 90)
        right_vector = [right_vector[0] * DeltaSeconds * 2, right_vector[1] * DeltaSeconds * 2]
        if pygame.key.get_pressed()[pygame.K_s]:
            ActiveCamera.LocationX += forward_vector[0]
            ActiveCamera.LocationY += forward_vector[1]
        if pygame.key.get_pressed()[pygame.K_z]:
            ActiveCamera.LocationX -= forward_vector[0]
            ActiveCamera.LocationY -= forward_vector[1]
        if pygame.key.get_pressed()[pygame.K_x]:
            ActiveCamera.LocationX += right_vector[0]
            ActiveCamera.LocationY += right_vector[1]
        if pygame.key.get_pressed()[pygame.K_a]:
            ActiveCamera.LocationX -= right_vector[0]
            ActiveCamera.LocationY -= right_vector[1]
        if pygame.key.get_pressed()[pygame.K_QUOTE]:
            ActiveCamera.Rotation -= 300 * DeltaSeconds
        if pygame.key.get_pressed()[pygame.K_PERIOD]:
            ActiveCamera.Rotation += 300 * DeltaSeconds

wall1 = Wall(PointsLocation=((-2, 2), (5, 2)))
wall2 = Wall(PointsLocation=((5, 2), (5, -0.2)), Color=(0, 100, 0))
wall3 = Wall(PointsLocation=((5, -0.2), (4.8, -0.2)), Color=(190, 45, 0))
wall4 = Wall(PointsLocation=((4.8, -0.2), (4.8, -1.5)), Color=(200, 50, 0))
wall5 = Wall(PointsLocation=((-2, 2), (-2, -1)), Color=(0, 0, 0))
walls = [wall1, wall2, wall3, wall4, wall5]
for i in range(0):
    walls.append(Wall(PointsLocation=((-1, 2), (-1, -1)), Color=(0, 0, 0)))
DrowDistance = 1000

def raycasting():
    r = ActiveCamera.FOV / (render_width - 1)
    screen.fill("white")
    for ray_rotation in range(render_width):
        if not fisheye:
            distance_to_screen = 1 / math.cos(math.radians(abs(ray_rotation * r - ActiveCamera.FOV/2)))
        else:
            distance_to_screen = 1
        lines_to_print = []
        ray_vector = RotationToVector(ray_rotation * r + ActiveCamera.Rotation - ActiveCamera.FOV/2)
        ray_vector = (ray_vector[0] * DrowDistance + ActiveCamera.LocationX, ray_vector[1] * DrowDistance + ActiveCamera.LocationY)
        for obj in walls:
            if intersection_point(obj.getPointsLocation(), (ActiveCamera.LocationX, ActiveCamera.LocationY, ray_vector[0], ray_vector[1])) is not None:
                x, y = intersection_point(obj.getPointsLocation(), (ActiveCamera.LocationX, ActiveCamera.LocationY, ray_vector[0], ray_vector[1]))
                dist = math.sqrt((x - ActiveCamera.LocationX) ** 2 + (y - ActiveCamera.LocationY) ** 2)
                if dist != 0:
                    sizeZ = (1 / dist * screen_height * 2) * distance_to_screen
                    color = []
                    for i in range(len(obj.Color)):
                        color.append(int(obj.Color[i] - dist/0.12))
                        if color[i] < 0: color[i] = 0
                    lines_to_print.append((sizeZ, color, ray_rotation))

        lines_to_print.sort(key=lambda x: x[0])
        for line in lines_to_print:
            try:
                screen.fill(line[1], (screen_width - line[2] * size - 1, int(((screen_height - line[0]) / 2) / size) * size, size, line[0]))
            except BaseException:
                ...


def intersection_point(line_segment, ray):
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

    def tick(self):
        for func in self.connection_functions:
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
            raycasting()
        else:
            print("ActiveCamera is not defined or is not <class 'Camera'>. ActiveCamera class:", type(ActiveCamera))
        pygame.display.flip()
        clock.tick(0)
    pygame.quit()
    sys.exit()
