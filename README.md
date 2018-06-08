## Constants

`toRad`: Conversion factor from HAU to radians

`toHAU`: Conversion factor from radians to HAU

`angleToRad`: Conversion factor from SM64 angle units to radians

`radToAngle`: Conversion factor from radians to SM64 angle units

`truncMultiplier`: Scale of PU grid and size of “unit squares”. 1 by default. Set to 4 for romhacks that use the extended boundaries patch.

## Classes

`position(x, y, z)`

A class containing three variables, `x`, `y`, and `z`. Used to define a point in three dimensional space.

`pos2D(x, z)`

A class containing two variables, `x` and `z`. Used to define a point on the XZ plane.

`triangle(x1, y1, z1, x2, y2, z2, x3, y3, z3)`

A class that defines a triangle in three dimensional space. Contains the subclasses `v1`, `v2`, `v3`, and `normal`. `v1`, `v2`, and `v3` are `position` objects which are the positions of the triangle’s three vertices, and  `normal` contains `x`, `y`, and `z`, which are the x, y, and z components of the triangle’s unit normal vector, and `offset` which is the plane’s signed distance from the origin.

`tri2D(x1, z1, x2, z2, x3, z3)`

A class that defines a two-dimensional triangle. Contains the subclasses `v1`, `v2`, and `v3`, which are `pos2D` objects that are the positions of the triangle’s three vertices.

`rectangle(xMin, xMax, zMin, zMax)`

Defines an axis-aligned rectangle on the XZ plane. Contains the subclasses `min` and `max`, which are the minimum (north-western) and maximum (south-eastern) vertices of the rectangle, and are `pos2D` objects.

`cylinder(x, y, z, radius, height)`

Defines a cylinder, where `x`, `y`, and `z` are the co-ordinates of the center of the base of the cylinder, and `radius` and `height` are the radius and height of the cylinder.

`apollonian(x1, z1, x2, z2, ratio)`

Contains two `pos2D` subclasses, `p1` and `p2`, and a variable `ratio`. Defines the set of points P such that the ratio of distance between P and p2 and distance between P and p1 is ratio R. Specifically, length(P p2) / length(P p1) = ratio. This set of points forms a circle in most cases, and a line if the ratio is 1.

### Compatibility

A `position` object can be used in place of a `pos2D` object.

A `triangle` object can be used in place of a `tri2D` object.

A `cylinder` object can be used in place of a `position` or `pos2D` object.

## Functions

### Syntax used for function arguments:

An argument presented plainly as a variable name is a required argument, such as `a` in `func(a)`. An argument presented with a value assignment, such as `b` in `func(b=2)` is an optional argument, and the value shown is its default value. In a function `func(a, b=2, c=3)`, you my call it like `func(1, c=4)` or like `func(1, 2, 4)`.

Important note: Throughout this document, “truncate” and “truncation” will be used to not only mean rounding towards zero to the nearest integer, but also placing the integer within the 16-bit integer range of -32768 to 32767.

### Movement functions

`applyMovement(position, speed, angle, qf=4, normalY=1)`

`position` is a `position` object that defines the starting position of the movement. `speed` and `angle` are the speed and angle the movement is done at (angle in HAU), `qf` is how many quarterframes the movement spans, and `normalY` is the Y component of the unit normal vector of the surface the position is on. Essentially, you'd use this if Mario's standing on a slope, which reduces his de facto speed.

Function returns a `position` object.

`applyJump(position, speed, angle, qf=1, jumpType=’single’)`

`position` is a `position` object that defines the starting position of the movement. `speed` and `angle` are the speed and angle the movement is done at (angle in HAU), and `qf` is how many quarterframes the movement spans (OJs will only ever be 1 qf long, so this variable only needs to be specified in non-OJ jumps).

`jumpType` can have three values:

`single`, the default value. In a single jump, VS is 42 + speed / 4

`double` is a double jump, whose VS is 52 + speed / 4

`squish` is a jump done while squished, whose VS is 21 + speed / 8

Function returns a `position` object.

`calcMovement(posA, posB, qf=4, normalY=1, puX=0, puZ=0, neg=True, signedAngle=False)`

`posA` and `posB` are `pos2D` objects that specify the start and end positions of the movement. `qf` and `normalY` set how many QFs the movement spans and the normal-Y of the ground the movement occurs on. `puX` and `puZ` are how many PUs on the X and Z axes the movement displaces Mario by. For example, `puX=1` and `puZ=-2` mean that the movement moves Mario 1 PU east and 2 PUs north.

`neg` sets whether or not the movement is done with negative speed, and `signedAngle` sets whether the angle should be presented as signed.

Function returns a class containing the variables `speed`, `angle`, and `error`, the difference between the integer angle shown and the actual angle from `posA` to `posB`.

`calcJump(posA, posB, qf=1, puX=0, puZ=0, neg=True, jumpType='single', signedAngle=False)`

`posA` is a `position object` and `posB` is a `pos2D` object, that together specify the start and end positions of the jump. `qf` sets how many QFs the jump spans. `puX` and `puZ` are how many PUs on the X and Z axes the jump displaces Mario by. For example, `puX=1` and `puZ=-2` mean that the jump moves Mario 1 PU east and 2 PUs north.

`neg` sets whether or not the jump is done with negative speed, and `signedAngle` sets whether the angle should be presented as signed.

`jumpType` can have three values:

`single`, the default value. In a single jump, VS is 42 + speed / 4

`double` is a double jump, whose VS is 52 + speed / 4

`squish` is a jump done while squished, whose VS is 21 + speed / 8

Function returns a class containing the variables `speed`, `angle`, `error` (the difference between the integer angle shown and the actual angle from `posA` to `posB`), and `y`, the (truncated) height after the jump.

### 2D Collision Functions

`inTriangle(position, triangle, rel=True)`

Finds if the position is inside the triangle on the x and z axes, returns a boolean. `rel` sets whether or not to truncate the position.

`position` is a `pos2D` object.

`triangle` is a `tri2D` object.

`inRectangle(position, rectangle, rel=True)`

Finds if the position is inside the (axis-aligned) rectangle on the x and z axes, returns a boolean. `rel` sets whether or not to use truncated co-ordinates, that is, to use relative position.

`position` is a `pos2D` object.

`rectangle` is a `rectangle` object.

`inPolygon(position, poly, rel=True)`

Finds if the position, a `pos2D` object, is inside the polygon defined by `poly`, a list of `pos2D` objects that define the vertices of the polygon. The polygon must be convex, and the list must be ordered correctly, though the direction (clockwise or counterclockwise) doesn’t matter. `rel` sets whether or not to use truncated co-ordinates for `position`, that is, to use relative position.

`distance(position1, position2, rel=True)`

Finds the lateral distance between the points `position1` and `position2`. rel sets whether or not to truncate the positions.

`position1` and `position2` are `pos2D` objects.

### 3D Collision Functions

`inCylinder(position, cylinder, rel=True)`

Finds if the position is inside the cylinder. `rel` sets whether or not to use truncated co-ordinates for the position, that is, to use relative position.

`position` is a `position` object.

`cylinder` is a `cylinder` object.

`distance3D(position1, position2, rel=True)`

Finds the three-dimensional distance between the points `position1` and `position2`. `rel` sets whether or not to truncate the positions.

`position1` and `position2` are `position` objects.

### Apollonian Circle Functions

`apollonianInTriangle(apollonian, tri, puX=0, puZ=0)`

Finds if the triangle `tri`, a `tri2D` object, intersects the apollonian circle, an `apollonian` object. `puX` and `puZ` offset `tri` by that many PUs on those axes.

`apollonianInRectangle(apollonian, rect, puX=0, puZ=0)`

Finds if the rectangle `rect`, a `rectangle` object, intersects the apollonian circle, an `apollonian` object. `puX` and `puZ` offset `tri` by that many PUs on those axes.

`apollonianInPolygon(apollonian, poly, puX=0, puZ=0)`

Finds if the polygon defined by `poly`, a list of `pos2D` objects that define the vertices of the polygon, intersects the apollonian circle, an `apollonian` object. `poly` must be convex for function to work correctly, though the vertices need not be in any particular order. `puX` and `puZ` offset `poly` by that many PUs on those axes.

### Floor Functions

`floorHeight(position, triangle)`

Returns the height of the plane defined by the `triangle` triangle, a `triangle` object, at the lateral position of `position`, a `pos2D` object. Note that this simply gives height of the plane defined by the triangle, which means this function does not check if the given position is actually over the triangle.

### Miscellaneous/Internal Use Functions

`truncate(n)`

Returns the truncated value of `n`, a number.