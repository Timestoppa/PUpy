import math
#constants and such
toRad = math.pi / 2048 #conversion factor from HAU to radians
toHAU = 2048 / math.pi #conversion factor from radians to HAU
angleToRad = math.pi / 32768 #conversion factor from SM64 angle units to radians
radToAngle = 32768 / math.pi #conversion factor from radians to SM64 angle units

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
    return int(((n + 32768) % 65536) - 32768)

#movement functions

def applyMovement(pos, speed, angle, qf=4, normalY=1): #function that handles non-OJ movement
    xMovement = speed * math.sin(angle * toRad) * normalY * qf / 4 #calculate x and z components of movement
    zMovement = speed * math.cos(angle * toRad) * normalY * qf / 4
    class outputPos: #create a class to output
        x = pos.x + xMovement   #apply previously calculated movements
        y = pos.y               #leaving the y axis unaffected
        z = pos.z + zMovement
    return outputPos

def applyJump(pos, speed, angle, qf=1, jumpType='single'): #function that handles OJs or hyper speed downward jumps
    xMovement = speed * math.sin(angle * toRad) * qf / 5 #x and z components of
    zMovement = speed * math.cos(angle * toRad) * qf / 5 #horizontal movement
    vs = 42 + speed / 4 #find base vertical speed
    if jumpType == 'double': vs += 10    #modify vertical speed to accomodate
    elif jumpType == 'squish': vs *= 0.5 #double jumps and squished jumps
    class outputPos:
        x = pos.x + xMovement       #unlike for the horizontal co-ordinates, we only account for QFs at the very end so that we don't have to account both when
        y = pos.y + (vs * qf / 4)   #calculating base vertical movement and when calculating modification from double and squished jumps, thus saving time by
        z = pos.z + zMovement       #only accounting for QFs once instead of twice
    return outputPos

#2d collision functions

def inTriangle(pos, tri, rel=True): #finds if point pos is inside the triangle tri
    px = pos.x
    pz = pos.z
    #truncate co-ordinates if relative is set to true
    if rel:
        px = truncate(px)
        pz = truncate(pz)
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
    #generate midpoint of a diagonal to find a point known to be inside the polygon
    known = pos2D((poly[0].x + poly[len(poly)//2].x)/2, (poly[0].z + poly[len(poly)//2].z)/2)
    pointInside = True
    #truncate if relative set
    x = pos.x
    z = pos.z
    if rel:
        x = truncate(x)
        z = truncate(z)
    for i in range(len(poly)):
        #find general form of line connecting vertices
        a = poly[i].z - poly[i-1].z
        b = poly[i-1].x - poly[i].x
        c = poly[i].x * poly[i-1].z - poly[i-1].x * poly[i].z
        #solve for c of both the known points and the points being tested, and multiply their differences to the side's c to xor their signs to ensure they are the same,
        #and thus on the same side of the side's line
        if ((-a * known.x) - (b * known.z) - c) * ((-a * pos.x) - (b * pos.z) - c) < 0:
            pointInside = False
    return pointInside

def distance(pos1, pos2, rel=True): #lateral distance between two points
    #truncate co-ordinates if relative is set to true
    if rel: return math.hypot(truncate(pos1.x) - truncate(pos2.x), truncate(pos1.z) - truncate(pos2.z))
    else: return math.hypot(pos1.x - pos2.x, pos1.z - pos2.z)

#3d collision functions

def inCylinder(pos, cylinder, rel=True):
    if rel: return distance(pos, cylinder) <= cylinder.radius and 0 <= truncate(pos.y) - truncate(cylinder.y) <= cylinder.height
    else: return distance(pos, cylinder, rel=False) <= cylinder.radius and 0 <= pos.y - cylinder.y <= cylinder.height

def distance3D(pos1, pos2, rel=True):
    if rel: return math.hypot(distance(pos1, pos2), truncate(pos1.y) - truncate(pos2.y))
    else: return math.hypot(distance(pos1, pos2, rel=False), pos1.y - pos2.y)

#apollonian circle functions

def apollonianInTriangle(apollonian, tri, puX=0, puZ=0):
    v1 = pos2D(tri.v1.x + 65536 * puX, tri.v1.z + 65536 * puZ)
    v2 = pos2D(tri.v2.x + 65536 * puX, tri.v2.z + 65536 * puZ)
    v3 = pos2D(tri.v3.x + 65536 * puX, tri.v3.z + 65536 * puZ)
    ratio1 = distance(v1, apollonian.p2) / distance(v1, apollonian.p1)
    ratio2 = distance(v2, apollonian.p2) / distance(v2, apollonian.p1)
    ratio3 = distance(v3, apollonian.p2) / distance(v3, apollonian.p1)
    return not((ratio1 - apollonian.ratio > 0) == (ratio2 - apollonian.ratio > 0) == (ratio3 - apollonian.ratio > 0)) or 0 in [ratio1, ratio2, ratio3]

def apollonianInRectangle(apollonian, rect, puX=0, puZ=0):
    v1 = pos2D(rect.min.x + 65536 * puX, rect.min.z + 65536 * puZ)
    v2 = pos2D(rect.min.x + 65536 * puX, rect.max.z + 65536 * puZ)
    v3 = pos2D(rect.max.x + 65536 * puX, rect.max.z + 65536 * puZ)
    v4 = pos2D(rect.max.x + 65536 * puX, rect.min.z + 65536 * puZ)
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
        point = pos2D(i.x + 65536 * puX, i.z + 65536 * puZ)
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
