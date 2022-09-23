from shapely.geometry import LineString, Polygon, MultiPoint
import numpy as np
from collections import deque

def x_from_y(a, b, yc):
    dx = b[0]-a[0]
    dy = b[1]-a[1]
    if dx==0:
        return np.ones(len(yc))*a[0]
    return (yc - a[1])*dx/dy + a[0]

def get_column(a, b, gap, height):
    maxy = max(a[1], b[1])
    miny = min(a[1], b[1])
    start = int(np.ceil(miny/gap))
    end = int(np.floor(maxy/gap)+1)
    ys = np.arange(start, end)*gap
    xs = x_from_y(a, b, ys)
    mask = np.ones(height)
    mask[start:end] = 0
    col = np.ma.array(np.zeros(height), mask=mask)
    col[start:end] = xs
    return col

def get_cols(shape, gap, thres):
    coords = shape.coords
    x, y = shape.xy
    height = int(np.floor(shape.bounds[3]/gap)+1)
    cols = []
    for i in range(len(coords)-1):
        a = coords[i]
        b = coords[i+1]
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        if abs(dy) > thres:
            col = get_column(a, b, gap, height)    
            cols.append(col)
    return np.ma.array(cols)

def sort_cols(cols):
    for i in range(cols.shape[1]):
        col = cols[:,i]
        valid_indexes = (col+1).nonzero()[0]
        sorted_indexes = valid_indexes[col[valid_indexes].argsort()]
        cols[[valid_indexes]] = cols[[sorted_indexes]]
 

def print_matrix(m):
    rowf = "{:3.2f} "* m.shape[1]
    for row in m:
        print(rowf.format(*row))

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    np.set_printoptions(precision=3)
    #shape = Polygon([(0,0), (10,0), (10, 10), (0, 10)])
    border = [(0, 0), (10, 0), (10, 10), (20, 10), (20, 5), (30, 5), (30, 40), (10,25), (0, 30), (3, 15)]
    holes = [[(5, 15), (15, 15), (15, 20), (5, 20)], [(20, 25), (25, 25), (25, 30)]]
    poly = Polygon(border, holes)

    gap = 5
    thres = 0
    cols = get_cols(poly.exterior, gap, thres)
    sort_cols(cols)
    print_matrix(cols)
    fig, ax = plt.subplots()
    x, y = poly.exterior.xy
    ax.plot(x, y, color="black", linewidth=3)

    ax.axis("equal")
    plt.show()