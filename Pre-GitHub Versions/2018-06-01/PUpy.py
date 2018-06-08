import math
#constants and such
toRad = math.pi / 2048 #conversion factor from HAU to radians
toHAU = 2048 / math.pi #conversion factor from radians to HAU
angleToRad = math.pi / 32768 #conversion factor from SM64 angle units to radians
radToAngle = 32768 / math.pi #conversion factor from radians to SM64 angle units

#functions
def movement(pos, speed, angle, qf, normalY): #function that handles non-OJ movement
    xMovement = speed * math.sin(angle * toRad) * normalY * qf / 4 #calculate x and z components of movement
    zMovement = speed * math.cos(angle * toRad) * normalY * qf / 4
    class outputPos: #create a class to output
        x = pos.x + xMovement   #apply previously calculated movements
        y = pos.y               #leaving the y axis unaffected
        z = pos.z + zMovement
        xTrunc = int(((x + 32768) % 65536) - 32768) #truncated and PU-relative positions
        yTrunc = int(((y + 32768) % 65536) - 32768)
        zTrunc = int(((z + 32768) % 65536) - 32768)
        xPU = round(int(x) / 65536) #which PU the position is in
        yPU = round(int(y) / 65536) #on all three axes
        zPU = round(int(z) / 65536)
    return outputPos
