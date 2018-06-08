import math
#constants and such
toRad = math.pi / 2048 #conversion factor from HAU to radians
toHAU = 2048 / math.pi #conversion factor from radians to HAU
angleToRad = math.pi / 32768 #conversion factor from SM64 angle units to radians
radToAngle = 32768 / math.pi #conversion factor from radians to SM64 angle units
truncMultiplier = 1 #scale of truncation, set to 4 for extended boundary patch

#classes

class position:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class pos2D:
    def __init__(self, x, z):
        self.x = x
        self.z = z

class triangle:
    def __init__(self, x1, y1, z1, x2, y2, z2, x3, y3, z3):
        #set vertices
        self.v1 = position(x1, y1, z1)
        self.v2 = position(x2, y2, z2)
        self.v3 = position(x3, y3, z3)
        #calculate normal
        #find the side vectors
        a = position(x2 - x1, y2 - y1, z2 - z1)
        b = position(x3 - x1, y3 - y1, z3 - z1)
        #compute cross product
        aCrossB = position(a.y * b.z - a.z * b.y, - (a.x * b.z - a.z * b.x), a.x * b.y - a.y * b.x)
        class normal:
            def __init__(self, aCrossB, x1, y1, z1):
                #find scale of cross product to aid in normalisation
                scale = math.hypot(math.hypot(aCrossB.x, aCrossB.y), aCrossB.z)
                #generate unit normal vector
                self.x = aCrossB.x / scale
                self.y = aCrossB.y / scale
                self.z = aCrossB.z / scale
                #find normal offset
                self.offset = -(self.x * x1 + self.y * y1 + self.z * z1)
        self.normal = normal(aCrossB, x1, y1, z1)

class tri2D:
    def __init__(self, x1, z1, x2, z2, x3, z3):
        self.v1 = pos2D(x1, z1)
        self.v2 = pos2D(x2, z2)
        self.v3 = pos2D(x3, z3)

class rectangle:
    def __init__(self, xMin, xMax, zMin, zMax):
        self.min = pos2D(xMin, zMin)
        self.max = pos2D(xMax, xMax)

class cylinder:
    def __init__(self, x, y, z, height, radius):
        self.x = x
        self.y = y
        self.z = z
        self.height = height
        self.radius = radius

class apollonian:
    def __init__(self, x1, z1, x2, z2, ratio):
        self.p1 = pos2D(x1, z1)
        self.p2 = pos2D(x2, z2)
        self.ratio = ratio

#miscellaneous/internal functions

def truncate(n): #emulation of in-game casting to 16-bit
    return int(((n / truncMultiplier + 32768) % 65536) - 32768) * truncMultiplier

#movement functions

def applyMovement(pos, speed, angle, qf=4, normalY=1): #function that handles non-OJ movement
    xMovement = speed * math.sin(angle * toRad) * normalY * qf / 4
    zMovement = speed * math.cos(angle * toRad) * normalY * qf / 4
    return position(pos.x + xMovement,
                    pos.y,
                    pos.z + zMovement)

def applyJump(pos, speed, angle, qf=1, jumpType='single'): #function that handles OJs or hyper speed downward jumps
    xMovement = speed * math.sin(angle * toRad) * qf / 5 #x and z components of
    zMovement = speed * math.cos(angle * toRad) * qf / 5 #horizontal movement
    vs = 42 + speed / 4 #find base vertical speed
    if jumpType == 'double': vs += 10    #modify vertical speed to accomodate
    elif jumpType == 'squish': vs *= 0.5 #double jumps and squished jumps
    return position(pos.x + xMovement,
                    truncate(pos.y + vs * qf / 4),
                    pos.z + zMovement)

def calcMovement(posA, posB, qf=4, normalY=1, puX=0, puZ=0, neg=True, signedAngle=False):
    xMovement = posB.x - posA.x + 65536 * truncMultiplier * puX #x and z components of
    zMovement = posB.z - posA.z + 65536 * truncMultiplier * puZ #horizontal movement
    moveSpeed = (math.hypot(xMovement, zMovement) * 4 / (qf * normalY)) * ((-1) ** neg) #find speed needed
    moveAngle = math.atan2(zMovement * ((-1) ** neg), xMovement * ((-1) ** neg)) * toHAU #find angle needed
    if moveAngle < 0 and not signedAngle:
        moveAngle += 4096 #unsign angle if necessary
    class movement:
        speed = moveSpeed
        angle = round(moveAngle)
        error = angle - moveAngle
    return movement

def calcJump(posA, posB, qf=1, puX=0, puZ=0, neg=True, jumpType='single', signedAngle=False):
    movement = calcMovement(posA, posB, qf=qf*0.8, puX=puX, puZ=puZ, signedAngle=signedAngle) #use calcMovement to find lateral movement of jump
    vs = 42 + movement.speed / 4 #find base vertical speed
    if jumpType == 'double': vs += 10    #modify vertical speed to accomodate
    elif jumpType == 'squish': vs *= 0.5 #double jumps and squished jumps
    jumpY = truncate(vs * qf / 4) #compute post-jump y position
    class movementOut:
        speed = movement.speed
        angle = movement.angle
        error = movement.error
        y = jumpY
    return movementOut

#2d collision functions

def inTriangle(pos, tri, rel=True): #finds if point pos is inside the triangle tri
    #truncate co-ordinates if relative is set to true
    if rel:
        px = truncate(pos.x)
        pz = truncate(pos.z)
    else:
        px = pos.x
        pz = pos.z
    #thanks to stackoverflow user andreasdr lmao
    area = 0.5 * (-tri.v1.z*tri.v2.x + tri.v3.z*(-tri.v1.x + tri.v2.x) + tri.v3.x*(tri.v1.z - tri.v2.z) + tri.v1.x*tri.v2.z)
    s = 1/(2 * area)*(tri.v3.z*tri.v2.x - tri.v3.x*tri.v2.z + (tri.v2.z - tri.v3.z)*px + (tri.v3.x - tri.v2.x)*pz)
    t = 1/(2 * area)*(tri.v3.x*tri.v1.z - tri.v3.z*tri.v1.x + (tri.v3.z - tri.v1.z)*px + (tri.v1.x - tri.v3.x)*pz)
    return s >= 0 and t >= 0 and t + s <= 1

def inRectangle(pos, rect, rel=True): #finds if point pos is in rectangle rec
    #truncate co-ordinates if relative is set to true
    if rel: return rect.min.x <= truncate(pos.x) <= rect.max.x and rect.min.z <= truncate(pos.z) <= rect.max.z
    else: return rect.min.x <= pos.x <= rect.max.x and rect.min.z <= pos.z <= rect.max.z

def inPolygon(pos, poly, rel=True): #finds if point pos is inside the polygon defined by the list of points
    pointInside = True
    #truncate if relative set
    if rel:
        x = truncate(pos.x)
        z = truncate(pos.z)
    else:
        x = pos.x
        z = pos.z
    i = 0
    while pointInside and i < len(poly):
        #find general form of line connecting vertices
        a = poly[i].z - poly[i-1].z
        b = poly[i-1].x - poly[i].x
        c = poly[i].x * poly[i-1].z - poly[i-1].x * poly[i].z
        #check that pos and another vertex are on the same side of the line
        if (a * x + b * z + c) * (a * poly[(i+1) % len(poly)].x + b * poly[(i+1) % len(poly)].z + c) < 0:
            pointInside = False
        i += 1
    return pointInside

def distance(pos1, pos2, rel=True): #lateral distance between two points
    #truncate co-ordinates if relative is set to true
    if rel: return math.hypot(truncate(pos1.x) - truncate(pos2.x), truncate(pos1.z) - truncate(pos2.z))
    else: return math.hypot(pos1.x - pos2.x, pos1.z - pos2.z)

#3d collision functions

def inCylinder(pos, cylinder, rel=True): #finds if position is inside a cylinder
    if rel: return distance(pos, cylinder) <= cylinder.radius and 0 <= truncate(pos.y) - truncate(cylinder.y) <= cylinder.height
    else: return distance(pos, cylinder, rel=False) <= cylinder.radius and 0 <= pos.y - cylinder.y <= cylinder.height

def distance3D(pos1, pos2, rel=True): #finds three-dimensional distance between positions
    if rel: return math.hypot(distance(pos1, pos2), truncate(pos1.y) - truncate(pos2.y))
    else: return math.hypot(distance(pos1, pos2, rel=False), pos1.y - pos2.y)

#apollonian circle functions

def apollonianInTriangle(apollonian, tri, puX=0, puZ=0): #finds if the apollonian circle passes through the triangle
    #get the three triangle vertices, adding on any pu offset specified
    v1 = pos2D(tri.v1.x + 65536 * truncMultiplier * puX, tri.v1.z + 65536 * truncMultiplier * puZ)
    v2 = pos2D(tri.v2.x + 65536 * truncMultiplier * puX, tri.v2.z + 65536 * truncMultiplier * puZ)
    v3 = pos2D(tri.v3.x + 65536 * truncMultiplier * puX, tri.v3.z + 65536 * truncMultiplier * puZ)
    #for each vertex, find its ratio of distances to the apollonian circle's defining points
    ratio1 = distance(v1, apollonian.p2) / distance(v1, apollonian.p1)
    ratio2 = distance(v2, apollonian.p2) / distance(v2, apollonian.p1)
    ratio3 = distance(v3, apollonian.p2) / distance(v3, apollonian.p1)
    return not((ratio1 - apollonian.ratio > 0) == (ratio2 - apollonian.ratio > 0) == (ratio3 - apollonian.ratio > 0)) or 0 in [ratio1, ratio2, ratio3]

def apollonianInRectangle(apollonian, rect, puX=0, puZ=0): #finds if the apollonian circle passes through the rectangle
    #get the four rectangle vertices, adding on any pu offset specified
    v1 = pos2D(rect.min.x + 65536 * truncMultiplier * puX, rect.min.z + 65536 * truncMultiplier * puZ)
    v2 = pos2D(rect.min.x + 65536 * truncMultiplier * puX, rect.max.z + 65536 * truncMultiplier * puZ)
    v3 = pos2D(rect.max.x + 65536 * truncMultiplier * puX, rect.max.z + 65536 * truncMultiplier * puZ)
    v4 = pos2D(rect.max.x + 65536 * truncMultiplier * puX, rect.min.z + 65536 * truncMultiplier * puZ)
    #for each vertex, find its ratio of distances to the apollonian circle's defining points
    ratio1 = distance(v1, apollonian.p2) / distance(v1, apollonian.p1)
    ratio2 = distance(v2, apollonian.p2) / distance(v2, apollonian.p1)
    ratio3 = distance(v3, apollonian.p2) / distance(v3, apollonian.p1)
    ratio4 = distance(v4, apollonian.p2) / distance(v4, apollonian.p1)
    return not((ratio1 - apollonian.ratio > 0) == (ratio2 - apollonian.ratio > 0) == (ratio3 - apollonian.ratio > 0) == (ratio4 - apollonian.ratio > 0)) or 0 in [ratio1, ratio2, ratio3, ratio4]

def apollonianInPolygon(apollonian, poly, puX=0, puZ=0):
    negativePresent = False
    positivePresent = False
    zeroPresent = False
    for i in poly:
        #for every point, compute its distance ratio's difference from the apollonian circle's ratio
        point = pos2D(i.x + 65536 * truncMultiplier * puX, i.z + 65536 * truncMultiplier * puZ)
        ratioDifference = distance(i, apollonian.p2) / distance(i, apollonian.p1) - apollonian.ratio
        if ratioDifference < 0:
            negativePresent = True
        elif ratioDifference == 0:
            zeroPresent = True
        else:
            positivePresent = True
    return zeroPresent or (negativePresent and positivePresent)

#floor height

def floorHeight(pos, tri):
    return -(tri.normal.offset / tri.normal.y) - (tri.normal.x * truncate(pos.x) / tri.normal.y) - (tri.normal.z * truncate(pos.z) / tri.normal.y)
