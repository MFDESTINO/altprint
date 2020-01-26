from shapely.geometry import LineString, MultiLineString, Point, MultiPoint
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

def rectilinear_fill(borders, angle, gap=0.5):
    """
    Generates an infill path, rectilinear, within the specified shape

    ARGS:
    borders_coords: List containing point tuples of the shape (list)
    gap: Gap between segments (float)
    angle: Angle of the infill segments in degrees. (float)

    RETURNS:
    path: Infill path. (LineString)
    """
    origin = borders.coords[0]
    borders = affinity.rotate(borders, angle)
    dif = [borders.bounds[0], borders.bounds[1]]
    borders=affinity.translate(borders, -dif[0],  -dif[1])
    prelines = _gen_lines(int(borders.bounds[2] / gap), borders.bounds[3], gap)
    intersection = prelines.intersection(borders)
    intersection = _refine(intersection)
    lines = _connect(intersection)
    path = _union_path(lines)
    path = linemerge(path)
    path = affinity.rotate(path, - angle, origin=borders.coords[0])
    borders = affinity.rotate(borders, - angle, origin=borders.coords[0])
    path = affinity.translate(path,  - borders.bounds[0] + origin[0],  - borders.bounds[1] + origin[1])
    borders = affinity.translate(borders,  - borders.bounds[0] + origin[0],  - borders.bounds[1] + origin[1])
    return [path]
