import numpy as np
from shapely.geometry import LineString, GeometryCollection, Polygon, MultiPoint, MultiLineString, Point
from shapely.affinity import translate
from shapely.ops import split
from shapely.ops import linemerge

def get_bounds(shape):
    minx = shape.bounds[0]
    miny = shape.bounds[1]
    maxx = shape.bounds[2]
    maxy = shape.bounds[3]
    return minx, miny, maxx, maxy


def get_point_heights(shape):
    y = []
    for coord in shape.coords:
        y.append(coord[1])
    y = list(set(y))  # remove doubles
    y.sort()
    return y


def add_mid_points(points):
    res = []
    for i in range(len(points)-1):
        res.append(points[i])
        res.append((points[i+1]+points[i])/2)
    return res


def get_lines_at_heights(heights, minx, maxx):
    lines = []
    for y in heights:
        lines.append(LineString([(minx, y), (maxx, y)]))
    return lines


def get_intersections(shape, horizontal_lines):
    intersections = []
    for line in horizontal_lines:
        intersection = shape.intersection(line)
        intersections.append(intersection)
    return intersections


def remove_overlaps(fill_segments):
    for i, line in enumerate(fill_segments):
        final_line = LineString(line.coords[-2:])
        for j, line2 in enumerate(fill_segments):
            first_line = LineString(line2.coords[:2])
            if final_line.within(first_line):
                fill_segments[i] = LineString(line.coords[:-2])
            elif first_line.within(final_line):
                fill_segments[j] = LineString(line2.coords[2:])
    return fill_segments


def fill_shape(border, horizontal_lines):
    x0 = []
    x1 = []
    y0 = []
    y1 = []
    for line in horizontal_lines:
        inter = line.intersection(border)
        if inter.bounds:
            minx, miny, maxx, maxy = get_bounds(inter)
            x0.append(minx)
            y0.append(miny)
            x1.append(maxx)
            y1.append(maxy)

    fill = []
    for i in range(len(x0)-1):
        fill.append(LineString([(x0[i], y0[i]), (x1[i], y1[i])]))
        if i % 2:
            line = LineString([(x0[i], y0[i]), (x0[i+1], y0[i+1])])
        else:
            line = LineString([(x1[i], y1[i]), (x1[i+1], y1[i+1])])
        fill.append(line)

    fill.append(LineString([(x0[-1], y0[-1]), (x1[-1], y1[-1])]))
    fill = linemerge(fill)
    return fill


def slice_shape(shape, gap):
    minx, miny, maxx, maxy = get_bounds(shape)
    heights = get_point_heights(shape.exterior)
    heights = add_mid_points(heights)
    horizontal_lines = get_lines_at_heights(heights, minx, maxx)
    intersections = get_intersections(shape, horizontal_lines)
    split_lines = []
    direction = False
    for i, intersection in enumerate(intersections):
        if type(intersection) == LineString:
            if i > 0:
                if type(intersections[i-1]) == MultiLineString:
                    lines = horizontal_lines[i-1]
                    if direction:
                        split_lines.append(lines.coords[1])
                        split_lines.append(lines.coords[0])
                        direction = False
                    else:
                        split_lines.append(lines.coords[0])
                        split_lines.append(lines.coords[1])
                        direction = True
            if i < len(horizontal_lines) - 1:
                if type(intersections[i+1]) == MultiLineString:
                    lines = horizontal_lines[i+1]
                    if direction:
                        split_lines.append(lines.coords[1])
                        split_lines.append(lines.coords[0])
                        direction = False
                    else:
                        split_lines.append(lines.coords[0])
                        split_lines.append(lines.coords[1])
                        direction = True
    if split_lines:
        return split(shape, LineString(split_lines))
    else:
        return [shape]


def rectilinear_fill(shape, gap):
    original_shape = shape
    final = slice_shape(shape, gap)
    heights = []
    for shape in final:
        minx, miny, maxx, maxy = get_bounds(shape)
        num_h_segments = int((maxy - miny)/gap) + 1
        heights.extend(list(np.linspace(miny, maxy, num_h_segments)))
    heights = list(set(heights))
    heights.sort()
    fill_segments = []
    minx, miny, maxx, maxy = get_bounds(Polygon(original_shape))
    horizontal_lines = get_lines_at_heights(heights, minx, maxx)
    for shape in final:
        fill_segments.append(fill_shape(shape, horizontal_lines))

    fill_segments = remove_overlaps(fill_segments)
    return fill_segments


