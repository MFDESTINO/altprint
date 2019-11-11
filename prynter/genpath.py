from shapely.geometry import LineString, LinearRing, MultiLineString, Point, MultiPoint
from shapely.ops import linemerge
from shapely import affinity
from collections import deque
import numpy as np

def _gen_lines(mx, my, gap):
    lines = []
    for i in range(mx + 1):
        lines.append(LineString([[i*gap,0], [i*gap,my]]))
    multi_line = MultiLineString(lines)
    return multi_line

def _connect(points):
    n = len(points)
    lines = []
    for i in range(int(n / 2)):
        lines.append(LineString([points[2 * i], points[2 * i + 1]]))
    lines = sorted(lines, key=lambda line: line.coords[0][0])
    multi_line = MultiLineString(lines)
    return multi_line

def _refine(collection):
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


def _union_path(lines):
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
    return path
