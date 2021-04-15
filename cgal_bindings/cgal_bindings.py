from y_monotone_partition.y_monotone_partition import y_monotone_partition as _y_monotone_partition
from y_monotone_partition.y_monotone_partition import DoubleVector
from shapely.geometry import Polygon


def to_vector(a):
    v = DoubleVector(len(a))
    for i, num in enumerate(a):
        v[i] = num
    return v


def y_monotone_partition(poly):
    x, y = poly.exterior.xy
    # the slice is to remove the last redundant point
    x_points = to_vector(x[:-1])
    y_points = to_vector(y[:-1])
    p = partition(x_points, y_points)
    polygon_number = int(len(p) / 2)
    polygons = []
    for i in range(polygon_number):
        coords = []
        x = p[i*2]
        y = p[i*2+1]
        for j in range(len(x)):
            coords.append((x[j], y[j]))
        polygon = Polygon(coords)
        if polygon.area > 1e-10:
            polygons.append(polygon)
    return polygons
