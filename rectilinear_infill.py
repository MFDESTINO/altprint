from shapely.geometry import LineString, Polygon, MultiLineString
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
    dy = b[1] - a[1]
    start = int(np.ceil(miny/gap))
    end = int(np.floor(maxy/gap)+1)
    ys = np.arange(start, end)*gap
    xs = x_from_y(a, b, ys)
    mask = np.ones(height)
    mask[start:end] = 0
    col = np.ma.array(np.zeros(height), mask=mask)
    col[start:end] = xs
    if dy > 0:
        fill_col = np.ma.array(np.zeros(height), mask=mask)
    else:
        fill_col = np.ma.array(np.ones(height), mask=mask)
    used_col = np.ma.array(np.zeros(height), mask=mask)
    return col, fill_col, used_col

def get_cols(shape, gap, thres):
    coords = shape.coords
    x, y = shape.xy
    height = int(np.floor(shape.bounds[3]/gap)+1)
    cols = []
    fill = []
    used = []
    for i in range(len(coords)-1):
        a = coords[i]
        b = coords[i+1]
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        if abs(dy) > thres:
            col, fill_col, used_col = get_column(a, b, gap, height)    
            cols.append(col)
            fill.append(fill_col)
            used.append(used_col)
    return np.ma.array(cols), np.ma.array(fill), np.ma.array(used)

def sort_cols(cols, fill, used):
    for i in range(cols.shape[1]):
        col = cols[:,i]
        valid_indexes = (col+1).nonzero()[0]
        sorted_indexes = valid_indexes[col[valid_indexes].argsort()]
        cols[[valid_indexes]] = cols[[sorted_indexes]]
        fill[[valid_indexes]] = fill[[sorted_indexes]]
        used[[valid_indexes]] = used[[sorted_indexes]]
 
def next_line(cols, fill, i, j, d):
    m, n = cols.shape
    if fill[i][j] == int(not d):
        return None
    if d:
        r = range(i, m)
    else:
        r = range(i, -1, -1)
    for k in r:
            if fill[k][j] == int(not d):
                return k

def next_con(cols, fill, i, j):
    m, n = cols.shape
    next_con = j+1
    if next_con < n:
        if not cols.mask[i][next_con]:
            return next_con
    return None

def find_path(cols, fill, used, i0, j0, d, gap):
    i, j = i0, j0
    path = [(cols[i][j], j*gap)]
    used[i][j] = 1
    while True:
        k = next_line(cols, fill, i, j, d)
        if k is not None:
            if used[k][j] == 0:
                used[k][j] = 1
                i = k
                d = not d
                path.append((cols[i][j], j*gap))
            else:
                return path
        else:
            return path
        l = next_con(cols, fill, i, j)
        if l is not None:
            if used[i][l] == 0:
                used[i][l] = 1
                j = l
                path.append((cols[i][j], j*gap))
            else:
                return path
        else:
            return path

def rectilinear_fill(cols, fill, used, gap):
    m, n = cols.shape
    paths = []
    d = True
    for i in range(m):
        for j in range(n):
            if used[i][j] == 0:
                path = find_path(cols, fill, used, i, j, d, gap)
                if len(path) > 1: #ignore points
                    paths.append(path)
    return MultiLineString(paths)

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

    gap = 3
    thres = 0
    cols, fill, used = get_cols(poly.exterior, gap, thres)
    sort_cols(cols, fill, used)
    paths = rectilinear_fill(cols, fill, used, gap)
    fig, ax = plt.subplots()
    x, y = poly.exterior.xy
    ax.plot(x, y, color="black", linewidth=3)

    for path in paths.geoms:
        x, y = path.xy
        ax.plot(x, y, linewidth=5)
    ax.axis("equal")
    plt.show()