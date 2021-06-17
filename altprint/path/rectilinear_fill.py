from shapely.geometry import Polygon, LineString, Point, MultiLineString, MultiPoint, GeometryCollection
from shapely.ops import linemerge, split
from shapely.affinity import rotate
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
    num_hlines = int((maxy - miny)/gap)
    heights = []
    for i in range(num_hlines):
        heights.append(gap*i+miny)
    #heights = list(np.linspace(miny, maxy, num_hlines))
    for h in heights:
        h_lines.append(LineString([(minx, h), (maxx, h)]))
    return h_lines


def get_intersections(polygon, hlines):
    intersections = []
    for line in hlines:
        intersection = [polygon.intersection(line)]
        if type(intersection[0]) == GeometryCollection:
            intersection = list(intersection[0])
        for geom in intersection:
            if type(geom) == Point:
                geom = LineString([geom, geom])
                intersections.append(geom)
            elif type(geom) == MultiLineString:
                merged = linemerge(geom)
                if type(merged) == LineString:
                    intersections.append(LineString([merged.coords[0], merged.coords[-1]]))
                else:
                    for line in merged:
                        intersections.append(line)
            elif type(geom) == LineString:
                intersections.append(geom)

    return intersections

def get_next_connection(point, connection_lines):
    for i in range(len(connection_lines)):
        line = connection_lines[i]
        if point.touches(line):
            if line.bounds[3] > point.coords[0][1]:
                return i
    return None

def get_next_line(point, lines):
    for i in range(len(lines)):
        line = lines[i]
        if point.touches(line):
            return i
    return None

def geom_to_list(geom): #multilinestring or linestring to list
    if type(geom) == LineString:
        return [geom]
    else:
        return list(geom)

def rectilinear_fill(shape, gap, angle):
    shape = rotate(shape, angle, origin=[0, 0])
    hlines = get_hlines(shape, gap)
    lines = get_intersections(shape, hlines)
    connection_lines = LineString(shape.exterior).difference(MultiLineString(lines))
    connection_lines = geom_to_list(connection_lines)

    for hole in shape.interiors:
        extra_connection_lines = LineString(hole).difference(MultiLineString(lines))
        extra_connection_lines = geom_to_list(extra_connection_lines)
        connection_lines.extend(extra_connection_lines)


    paths = []
    while(len(lines)):
        path = lines.pop(0)
        index = get_next_connection(Point(path.coords[-1]), connection_lines)
        while(index != None):
            next_line = connection_lines.pop(index)
            path = linemerge([path, next_line])
            index = get_next_line(Point(path.coords[-1]), lines)
            if index == None:
                #remove the last connection
                path = LineString(path.coords[:-1*(len(next_line.coords)-1)])
                break
            next_line = lines.pop(index)
            path = linemerge([path, next_line])
            index = get_next_connection(Point(path.coords[-1]), connection_lines)
        paths.append(path)
    paths_rotated = []
    for path in paths:
        paths_rotated.append(rotate(path, -angle, origin=[0,0]))
    return paths_rotated


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    ax = plt.subplot()
    border = [(0, 0), (10, 0), (10, 10), (20, 10), (20, 5), (30, 5), (30, 40), (10,25), (0, 30)]
    holes = [[(5, 15), (15, 15), (15, 20), (5, 20)], [(20, 25), (25, 25), (25, 30)]]
    shape = Polygon(border, holes)
    paths = rectilinear_fill(shape, 0.5, 0)

    x, y = shape.exterior.xy
    ax.plot(x, y, color="gray")
    ax.axis('equal')

    for path in paths:
        x, y = path.xy
        ax.plot(x, y, linewidth=2)
    plt.show()
