from shapely.ops import split
from shapely.geometry import LineString, MultiLineString

def retract(path, ratio):
    x, y = path.xy
    A = (x[0], y[0])
    B = (x[-1], y[-1])
    C = (A[0] + ratio*(B[0]-A[0]), A[1] + ratio*(B[1]-A[1]))
    flex_path = LineString([A, C])
    retract_path = LineString([C, B])
    return flex_path, retract_path

def split_lines(lines, spliter):
    final = []
    for line in lines:
        for i in list(split(line, spliter)):
            if type(i) == LineString:
                final.append(i)
            else:
                print("not linestring")
    return final

def split_by_regions(lines, regions):
    final = list(lines)
    for region in regions:
        final = split_lines(final, region)
    return MultiLineString(final)
