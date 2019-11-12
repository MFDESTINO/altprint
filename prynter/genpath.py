from shapely.geometry import LineString, LinearRing, MultiLineString, Point, MultiPoint
from shapely.ops import linemerge
from shapely import affinity
from collections import deque
import numpy as np

def _gen_lines(mx, my, gap):
    """
    (internal)
    Generate parallel lines

    ARGS:
    mx: parallel lines number (int)
    my: parallel lines height (float)
    gap: distance between lines (float)

    RETURNS:
    MultiLineString containing the parallel lines. (MultLineString)
    """
    lines = []
    for i in range(mx + 1):
        lines.append(LineString([[i*gap,0], [i*gap,my]]))
    multi_line = MultiLineString(lines)
    return multi_line

def _refine(collection):
    """
    (internal)
    Remove double points and turn lines into a pair of points.

    ARGS:
    collection: GeometryCollection containg all lines and points of the path

    RETURNS:
    MultiPoint containg the refined points.
    """
    refined = []
    for geom in collection:
        if type(geom) != Point:
            refined.append(Point(geom.coords[0]))
            refined.append(Point(geom.coords[-1]))
        else:
            refined.append(geom)
    if refined[0].coords[0][0] != refined[1].coords[0][0]:
        refined.pop(0)
    multi_point = MultiPoint(refined)
    return multi_point

def _connect(points):
    """
    (internal)
    Connect the points of parallel lines, creating an continuous path

    ARGS:
    points: MultiPoint containing all points to be connected (MultiPoint)

    RETURNS:
    MultiLineString containing the path (MultiLineString)
    """
    n = len(points)
    lines = []
    for i in range(int(n / 2)):
        lines.append(LineString([points[2 * i], points[2 * i + 1]]))
    lines = sorted(lines, key=lambda line: line.coords[0][0])
    multi_line = MultiLineString(lines)
    return multi_line

def _union_path(lines):
    """
    (internal)
    Turn an unconnected MultiLineString into a continuous path

    ARGS:
    lines: MultiLineString containg the unconnected path (MultiLineString)

    RETURNS:
    MultiLineString containing the continuous path (MultiLineString)
    """
    n = len(lines) - 1
    path = []
    for i in range(n):
        if i % 2:
            path.append(lines[i])
            path.append(LineString([lines[i].coords[0], lines[i+1].coords[0]]))
        else:
            path.append(lines[i])
            path.append(LineString([lines[i].coords[-1], lines[i+1].coords[-1]]))
    path.append(lines[-1])
    multi_line = MultiLineString(path)
    return multi_line

def contour(shape, L):
    """
    Generate a contour line from L milimeters of the shape object.

    ARGS:
    shape: MultiLineString of the shape (MultiLineString)
    L: distance of the contour from shape. Positive numbers means external
    contours, negative numbers means internal contours (float)

    RETURNS:
    list containing the contour segments. (list)
    """
    shape_border = []
    for i in range(len(shape)):
        A = shape[i-2]
        B = shape[i-1]
        C = shape[i]

        u = LineString([A,B])
        v = LineString([B,C])

        ux = B[0] - A[0]
        uy = B[1] - A[1]
        vx = C[0] - B[0]
        vy = C[1] - B[1]

        udx = L*uy/u.length
        udy = L*ux/u.length
        vdx = L*vy/v.length
        vdy = L*vx/v.length

        ut = affinity.translate(u,  udx, -udy)
        vt = affinity.translate(v, vdx, -vdy)
        Ax = ut.coords[0][0]
        Ay = ut.coords[0][1]
        Bx = ut.coords[1][0]
        By = ut.coords[1][1]
        Cx = vt.coords[0][0]
        Cy = vt.coords[0][1]
        Dx = vt.coords[1][0]
        Dy = vt.coords[1][1]

        a = np.array([[Ay-By, Bx-Ax], [Cy-Dy, Dx-Cx]])
        b = np.array([Bx*Ay-Ax*By,  Dx*Cy-Cx*Dy])
        x = np.linalg.solve(a, b)

        shape_border.append(x)
    shape_border = deque(shape_border)
    shape_border.rotate(-1)
    return list(shape_border)

def retract(x, y, f):
    """
    Splits an AB segment from a C point, between A and B. Used for creating
    an recovery zone on variable flow bridges.

    ARGS:
    x: list contaning x points from the segment (list)
    y: list contaning y points from the segment (list)
    f: factor that determines where the segment will be splited. (float)

    RETURNS:
    Tuple containg the two new segments. (tuple)
    """
    A = [x[0], y[0]]
    B = [x[1], y[1]]
    C = [A[0] + f*(B[0]-A[0]), A[1] + f*(B[1]-A[1])]
    acx = [A[0], C[0]]
    acy = [A[1], C[1]]
    cbx = [C[0], B[0]]
    cby = [C[1], B[1]]
    AC = [acx, acy]
    CB = [cbx, cby]
    return AC, CB

def gen_square(borders_coords, gap, raster_ang):
    """
    Generates an infill path, rectilinear, within the specified shape

    ARGS:
    borders_coords: List containing point tuples of the shape (list)
    gap: Gap between segments (float)
    raster_ang: Angle of the infill segments in degrees. (float)

    RETURNS:
    path: Infill path. (LineString)
    """
    borders = LinearRing(borders_coords)
    origin = borders_coords[0]
    borders = affinity.rotate(borders, raster_ang)
    dif = [borders.bounds[0], borders.bounds[1]]
    borders=affinity.translate(borders, -dif[0],  -dif[1])
    prelines = _gen_lines(int(borders.bounds[2] / gap), borders.bounds[3], gap)
    intersection = prelines.intersection(borders)
    intersection = _refine(intersection)
    lines = _connect(intersection)
    path = _union_path(lines)
    path = linemerge(path)
    path = affinity.rotate(path, - raster_ang, origin=borders.coords[0])
    borders = affinity.rotate(borders, - raster_ang, origin=borders.coords[0])
    path = affinity.translate(path,  - borders.bounds[0] + origin[0],  - borders.bounds[1] + origin[1])
    borders = affinity.translate(borders,  - borders.bounds[0] + origin[0],  - borders.bounds[1] + origin[1])
    print(type(path))
    return path
