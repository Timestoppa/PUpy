import math
#constants and such
toRad = math.pi / 2048 #conversion factor from HAU to radians
toHAU = 2048 / math.pi #conversion factor from radians to HAU
angleToRad = math.pi / 32768 #conversion factor from SM64 angle units to radians
radToAngle = 32768 / math.pi #conversion factor from radians to SM64 angle units

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

def applyOJ(pos, speed, angle, qf=1, jumpType='single'): #function that handles OJs or hyper speed downward jumps
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
