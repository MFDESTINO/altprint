from shapely.geometry import LineString, Polygon, Point, MultiLineString, MultiPolygon, MultiPoint
from shapely.ops import split, linemerge, snap
from shapely.affinity import rotate
from altprint.path.partition import partition_shape_with_regions
import numpy as np


def get_bounds(polygon):
    minx = polygon.bounds[0]
    miny = polygon.bounds[1]
    maxx = polygon.bounds[2]
    maxy = polygon.bounds[3]
    return minx, miny, maxx, maxy


def get_hlines(polygon, gap):
    h_lines = []
    minx, miny, maxx, maxy = get_bounds(polygon)
    num_hlines = int((maxy - miny)/gap) + 1
    heights = list(np.linspace(miny, maxy, num_hlines))
    for h in heights:
        h_lines.append(LineString([(minx, h), (maxx, h)]))
    return h_lines


def get_intersections(polygon, hlines):
    intersections = []
    for line in hlines:
        intersection = polygon.intersection(line)
        if type(intersection) == Point:
            intersection = LineString([intersection, intersection])
        if type(intersection) == MultiLineString:
            merged = linemerge(intersection)
            intersection = LineString([merged.coords[0], merged.coords[-1]])
        intersections.append(intersection)
    return intersections


def get_path(border, intersections):
    path = []
    for i in range(len(intersections)-1):
        path.append(intersections[i])
        bottom_coords = sorted(intersections[i].coords, key=lambda x: x[0])
        upper_coords = sorted(intersections[i+1].coords, key=lambda x: x[0])
        if i % 2:
            pts = [bottom_coords[0], upper_coords[0]]
        else:
            pts = [bottom_coords[1], upper_coords[1]]
        mp_tolerance = MultiPolygon([Point(pts[0]).buffer(0.001), Point(pts[1]).buffer(0.001)])
        mp = MultiPoint([Point(pts[0]), Point(pts[1])])
        splited = split(border, mp_tolerance)
        splited = sorted(splited, key=lambda geom: geom.length)
        for geom in splited:
            if geom.length > 0.003:
                path.append(geom)
                break
    path.append(intersections[-1])
    return path


def snap_and_merge_path(path, tolerance=0.003):
    '''
    snap the vertices of the connection lines to fit the horizontal lines,
    so when merging there'll be no tolerance error.
    '''
    path_new = []
    for i in range(len(path)-1):
        if not i % 2:
            path_new.append(path[i])
        else:
            line = snap(path[i], path[i-1], tolerance)
            line = snap(line, path[i+1], tolerance)
            path_new.append(line)
    path_new.append(path[-1])
    path_new = linemerge(path_new)
    if type(path_new) == MultiLineString:
        path_new = list(path_new)
    elif type(path_new) == LineString:
        path_new = [path_new]
    return path_new

def fill_monotone_polygon(polygon, rgap):
    border = polygon.exterior

def remove_overlaps(infill):
    overlaps = []
    for i in range(len(infill)):
        for j in range(i, len(infill)):
            if i != j:
                overlap = infill[i].intersection(infill[j])
                if overlap:
                    overlaps.append(overlap)

    infill = MultiLineString(infill)
    overlaps2 = MultiLineString(overlaps)
    infill_without_overlaps = list(infill.difference(overlaps2))
    infill_without_overlaps.extend(overlaps)
    return infill_without_overlaps

def rectilinear_fill(shape, regions = [], angle=0, rgap=0.5, egap=0, igap=0.5, pgap=0):
    shape=rotate(shape, -angle, origin=[0, 0])
    polygons = partition_shape_with_regions(shape, regions, egap, igap, pgap)
    infill = []
    for polygon in polygons:
        hlines = get_hlines(polygon, rgap)
        intersections = get_intersections(polygon, hlines)
        path = get_path(LineString(polygon.exterior), intersections)
        infill.extend(snap_and_merge_path(path))
    infill = remove_overlaps(infill)
    infill = sorted(infill, key=lambda line: line.bounds[0])
    infill = sorted(infill, key=lambda line: line.bounds[1])
    infill_rotated = []
    for line in infill:
        infill_rotated.append(rotate(line, angle, origin=[0,0]))
    return infill_rotated
