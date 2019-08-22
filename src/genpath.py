from shapely.geometry import LineString, LinearRing, MultiLineString, Point, MultiPoint
from shapely.ops import linemerge
from shapely import affinity
from collections import deque
import numpy as np

def gen_lines(mx, my, gap):
    lines = []
    for i in range(mx + 1):
        lines.append(LineString([[i*gap,0], [i*gap,my]]))
    multi_line = MultiLineString(lines)
    return multi_line

def connect(points):
    n = len(points)
    lines = []
    for i in range(int(n / 2)):
        lines.append(LineString([points[2 * i], points[2 * i + 1]]))
    lines = sorted(lines, key=lambda line: line.coords[0][0])
    multi_line = MultiLineString(lines)
    return multi_line

def refine(collection):
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


def union_path(lines):
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

def gen_square(borders_coords, gap, raster_ang):
    borders = LinearRing(borders_coords)
    borders = affinity.rotate(borders, raster_ang)
    borders=affinity.translate(borders, borders.bounds[0] * -1,  borders.bounds[1] * -1)
    prelines = gen_lines(int(borders.bounds[2] / gap), borders.bounds[3], gap)
    intersection = prelines.intersection(borders)
    intersection = refine(intersection)
    lines = connect(intersection)
    path = union_path(lines)
    path = linemerge(path)
    path = affinity.rotate(path, raster_ang * -1)
    path = affinity.translate(path, path.bounds[0] * -1, path.bounds[1] * -1)

    return path

def centralize(path, bed_x, bed_y):
    path = affinity.translate(path, path.bounds[0] * -1,  path.bounds[1] * -1)
    dx = bed_x / 2 - path.bounds[2] / 2
    dy = bed_y / 2 - path.bounds[3] / 2
    path = affinity.translate(path, dx, dy)
    return path
