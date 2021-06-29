from shapely.geometry import Polygon, LineString, Point, MultiLineString, MultiPoint, GeometryCollection, LinearRing
from shapely.ops import linemerge, split
from shapely.affinity import rotate
import numpy as np
from pulp import *

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
    heights = []
    for i in range(num_hlines):
        heights.append(gap*i+miny)
    for h in heights:
        h_lines.append(LineString([(minx, h), (maxx, h)]))
    return h_lines


def get_intersections(polygon, hlines):
    intersections = []
    hlines_by_heights = []
    for i, line in enumerate(hlines):
        hlines_by_heights.append([])
        intersection = [polygon.intersection(line)]
        if type(intersection[0]) == GeometryCollection:
            intersection = list(intersection[0])
        for geom in intersection:
            if type(geom) == MultiLineString:
                merged = linemerge(geom)
                if type(merged) == LineString:
                    line = LineString([merged.coords[0], merged.coords[-1]])
                    intersections.append(line)
                    hlines_by_heights[i].append(line)
                else:
                    for line in merged:
                        intersections.append(line)
                        hlines_by_heights[i].append(line)
            elif type(geom) == LineString:
                intersections.append(geom)
                hlines_by_heights[i].append(line)

    return intersections, hlines_by_heights


def geom_to_list(geom): #multilinestring or linestring to list
    if type(geom) == LineString:
        return [geom]
    else:
        lines = list(geom)
        return lines

def remove_same_height_lines(hlines, clines):
    filtered_lines = []
    for line in clines:
        a = Point(line.coords[0])
        b = Point(line.coords[-1])
        if not a.coords[0][1] == b.coords[0][1]:
            for hline in hlines:
                if a.touches(hline):
                    for hline2 in hlines:
                        if b.touches(hline2):
                            filtered_lines.append(line)
                            break


    return filtered_lines

def get_lines(shape, gap):
    hlines = get_hlines(shape, gap)
    lines, hlines_by_heights = get_intersections(shape, hlines)
    connection_lines = LinearRing(shape.exterior).difference(MultiLineString(hlines))
    connection_lines = geom_to_list(connection_lines)
    for hole in shape.interiors:
        extra_connection_lines = LinearRing(hole).difference(MultiLineString(hlines))
        extra_connection_lines = geom_to_list(extra_connection_lines)
        connection_lines.extend(extra_connection_lines)
    connection_lines = remove_same_height_lines(lines, connection_lines)
    return lines, connection_lines, hlines_by_heights

def get_connections_by_heights(clines, polygon, gap):
    minx, miny, maxx, maxy = get_bounds(polygon)
    num_hlines = int((maxy - miny)/gap) + 1
    edges = linemerge(MultiLineString(clines))

    clines_by_heights = []
    theta = np.ones((len(edges), num_hlines))
    for i, edge in enumerate(edges):
        clines_by_heights.append([])
        for j in range(num_hlines):
            clines_by_heights[i].append(None)
        for line in clines:
            if line.within(edge):
                j = int((line.bounds[1]-miny)/gap)
                clines_by_heights[i][j] = line
                theta[i][j] = 0
    return clines_by_heights, theta

def get_c(hlines_by_heights, clines_by_heights):
    c = np.zeros((len(clines_by_heights), len(clines_by_heights), len(clines_by_heights[0])))
    for i in range(len(c)):
        for j in range(len(c[0])):
            for k in range(len(c[0][0])):
                a = clines_by_heights[i][k]
                b = clines_by_heights[j][k]
                if a != None and b != None:
                    for hline in hlines_by_heights[k]:
                        if a.touches(hline) and b.touches(hline):
                            c[i][j][k] = 1
                            break
    return c

def get_x(clines):
    x = []
    for i in range(len(clines)):
        x.append([])
        for j in range(len(clines[i])):
            x[i].append("x{}.{}".format(i, j))
    return x

def get_all(shape, gap):
    hlines, pre_clines, hlines_by_heights = get_lines(shape, gap)
    clines, theta = get_connections_by_heights(pre_clines, shape, gap)
    if not clines:
        return None, None, None, None, None
    c = get_c(hlines_by_heights, clines)
    x = get_x(clines)
    return hlines, clines, theta, c, x

def rectilinear_optimal(shape, gap, angle):
    hlines, clines, theta, c, x = get_all(shape, gap)
    if not clines:
        return [], None, None, 0, 0, 0, 0
    prob = LpProblem("Problema_Teste",LpMaximize)

    xf = [j for i in x for j in i]
    z = LpVariable.dicts("LC",xf,cat = 'Binary')

    prob += lpSum(z)

    '''restrição de não poder usar uma linha de conexão que não existe'''
    for i in range(len(x)):
        for j in range(len(x[i])-1):
            prob += z[x[i][j]] + z[x[i][j+1]] <= 1
            prob += theta[i][j] + z[x[i][j]] <= 1
        prob += theta[i][-1] + z[x[i][-1]] <= 1

    ''' restrição não poder ir para duas linhas de conexão que possuem uma ligação'''
    for i in range(len(c)):
        for j in range(i+1,len(c[i])):
            for k in range(len(c[i][j])):
                if(c[i][j][k] != 0):
                    prob += c[i][j][k] * (z[x[i][k]] + z[x[j][k]]) <= 1
    prob.solve(PULP_CBC_CMD(msg=0));
    tempo = prob.solutionTime
    num_restr = len(prob.constraints)
    num_var = len(prob._variables)

    vecSol = [v.varValue for v in prob.variables()]

    valor = value(prob.objective)

    selected_lines = []
    for v in prob.variables():
        if v.varValue == 1:
            i = int(v.name[4:].split(".")[0])
            j = int(v.name[4:].split(".")[1])
            selected_lines.append(clines[i][j])

    selected_lines.extend(hlines)
    paths = linemerge(MultiLineString(selected_lines))
    if type(paths) == LineString:
        return [paths], clines, hlines, tempo, num_var, num_restr, valor
    else:
        return list(paths), clines, hlines, tempo, num_var, num_restr, valor
