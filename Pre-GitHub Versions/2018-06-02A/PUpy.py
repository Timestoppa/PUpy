import math
#constants and such
toRad = math.pi / 2048 #conversion factor from HAU to radians
toHAU = 2048 / math.pi #conversion factor from radians to HAU
angleToRad = math.pi / 32768 #conversion factor from SM64 angle units to radians
radToAngle = 32768 / math.pi #conversion factor from radians to SM64 angle units

#functions
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

def inTriangle(pos, tri): #finds if point pos is inside the triangle tri
    #thanks to stackoverflow user andreasdr lmao
    area = 0.5 * (-tri.v1.z*tri.v2.x + tri.v3.z*(-tri.v1.x + tri.v2.x) + tri.v3.x*(tri.v1.z - tri.v2.z) + tri.v1.x*tri.v2.z)
    s = 1/(2 * area)*(tri.v3.z*tri.v2.x - tri.v3.x*tri.v2.z + (tri.v2.z - tri.v3.z)*pos.x + (tri.v3.x - tri.v2.x)*pos.z)
    t = 1/(2 * area)*(tri.v3.x*tri.v1.z - tri.v3.z*tri.v1.x + (tri.v3.z - tri.v1.z)*pos.x + (tri.v1.x - tri.v3.x)*pos.z)
    return s >= 0 and t >= 0 and t + s <= 1
