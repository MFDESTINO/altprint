import matplotlib.pyplot as plt
from shapely.geometry import LineString, GeometryCollection, Polygon, MultiPoint, MultiLineString, Point
from shapely.affinity import translate
from shapely.ops import split
from shapely.ops import linemerge

def fill(border, gap, nlines, lines0):
    border = LineString(border.exterior)


    border_buffer = border.buffer(0.1)



    lines1 = []
    for i in range(nlines):
        line = lines0[i]
        inter = line.intersection(border)
        if type(inter) == Point:
            lines1.append([inter.coords[0], inter.coords[0]])
        if type(inter) == LineString:
            if len(inter.coords) > 1:
                lines1.append([inter.coords[0], inter.coords[1]])
        if type(inter) == MultiPoint:
            lines1.append([inter[0].coords[0], inter[1].coords[0]])
        if type(inter) == MultiLineString:
            inter = linemerge(inter)
            lines1.append([inter.coords[0], inter.coords[-1]])
        if type(inter) == GeometryCollection:
            asd = []
            for geom in inter:
                if type(geom) == LineString:
                    asd.append(geom.coords[0])
                    asd.append(geom.coords[1])
                if type(geom) == Point:
                    asd.append(geom.coords[0])
            asd = sorted(asd, key=lambda line: line[0])
            lines1.append([asd[0], asd[-1]])

    lines2 = []
    mov = 0
    a = False
    lines2.append([])
    for i in range(len(lines1)-1):
        lines2[mov].append(LineString(lines1[i]))
        if i%2:
            line = LineString([lines1[i][0], lines1[i+1][0]])
        else:
            line = LineString([lines1[i][1], lines1[i+1][1]])

        if line.within(border_buffer):
            lines2[mov].append(line)
        else:
            lines2.append([])
            mov += 1

    lines2[mov].append(LineString(lines1[-1]))

    for i in range(len(lines2)):
        lines2[i] = linemerge(lines2[i])
    return lines2


def slice_shape(shape, gap):
    minx = shape.bounds[0]
    miny = shape.bounds[1]
    maxx = shape.bounds[2]
    maxy = shape.bounds[3]

    nlines = int((maxx - minx)/gap)


    y_index = []
    for coord in shape.exterior.coords:
        y_index.append(coord[1])
    y_index = list(set(y_index))
    y_index.sort()

    division_lines = [LineString([(minx, y_index[0]),(maxx, y_index[0])])]
    for i in range(len(y_index)-1):
        y = (y_index[i]+y_index[i+1])/2
        division_lines.append(LineString([(minx, y),(maxx, y)]))
        y = y_index[i+1]
        division_lines.append(LineString([(minx, y),(maxx, y)]))


    intersections = []
    for line in division_lines:
        intersection = shape.intersection(line)
        intersections.append(intersection)
    split_lines = []
    direction = False
    for i, intersection in enumerate(intersections):
        if type(intersection) == LineString:
            if i > 0:
                if type(intersections[i-1]) == MultiLineString:
                    dl = division_lines[i-1]
                    if direction:
                        split_lines.append(dl.coords[1])
                        split_lines.append(dl.coords[0])
                        direction = False
                    else:
                        split_lines.append(dl.coords[0])
                        split_lines.append(dl.coords[1])
                        direction = True
            if i < len(division_lines) - 1:
                if type(intersections[i+1]) == MultiLineString:
                    dl = division_lines[i+1]
                    if direction:
                        split_lines.append(dl.coords[1])
                        split_lines.append(dl.coords[0])
                        direction = False
                    else:
                        split_lines.append(dl.coords[0])
                        split_lines.append(dl.coords[1])
                        direction = True
    if split_lines:
        return split(shape, LineString(split_lines))
    else:
        return [shape]

def rectilinear_fill(shape, gap):
    minx = shape.bounds[0]
    miny = shape.bounds[1]
    maxx = shape.bounds[2]
    maxy = shape.bounds[3]
    nlines = int((maxy - miny)/gap) + 1
    lines0 = []
    for i in range(nlines):
        lines0.append(LineString([(minx, i*gap+miny), (maxx, i*gap+miny)]))

    final = slice_shape(shape, gap)
    final_fill = []

    for shape in final:
        for line in fill(shape, gap, nlines, lines0):
            final_fill.append(line)

    for i, line in enumerate(final_fill):
        final_line = LineString([line.coords[-2], line.coords[-1]])
        for j, line2 in enumerate(final_fill):
            first_line = LineString([line2.coords[0], line2.coords[1]])
            if final_line.within(first_line):
                final_fill[i] = final_fill[i].difference(final_fill[j])
            if first_line.within(final_line):
                final_fill[j] = final_fill[j].difference(final_fill[i])
    return final_fill

if __name__ == "__main__":

    ax = plt.subplot()

    shape_border = [(0,0), (5, 0), (10, 5), (15, 5), (15, 0), (20,0), (20,18), (15,20), (10,10), (5, 10), (5, 20), (0, 20),(0,0)]
    
    shape = Polygon(shape_border)

    gap = 0.5
    final_fill = rectilinear_fill(shape, gap)
    for line in final_fill:
        x, y = line.xy
        ax.plot(x, y)

    ax.grid(True)
    plt.axis('equal')
    plt.show()
