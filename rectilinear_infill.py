from shapely.geometry import LineString, Polygon, MultiPoint
import numpy as np

def x_from_y(a, b, yc):
    dx = b[0]-a[0]
    dy = b[1]-a[1]
    if dx==0:
        return np.ones(len(yc))*a[0]
    return (yc - a[1])*dx/dy + a[0]

def get_connection_lines(shape):
    coords = shape.coords
    connection_lines = []
    for i in range(len(coords)-1):
        a = coords[i]
        b = coords[i+1]
        dy = (b[1] - a[1])
        ys = np.array([])
        if dy > thres: #b > a
            ys = np.arange(np.ceil(a[1]/gap), np.floor(b[1]/gap)+1)*gap
        if dy < -thres: #b < a
            ys = np.arange(np.floor(a[1]/gap), np.ceil(b[1]/gap-1), -1)*gap
        xs = x_from_y(a, b, ys)
        points = list(zip(xs, ys))
        for i in range(len(points)-1):
            connection_lines.append(LineString([points[i], points[i+1]]))
    return connection_lines

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    #shape = Polygon([(0,0), (10,0), (10, 10), (0, 10)])
    border = [(0, 0), (10, 0), (10, 10), (20, 10), (20, 5), (30, 5), (30, 40), (10,25), (0, 30), (3, 15)]
    holes = [[(5, 15), (15, 15), (15, 20), (5, 20)], [(20, 25), (25, 25), (25, 30)]]
    poly = Polygon(border, holes)

    gap = 2
    thres = 0
    connection_lines = get_connection_lines(poly.exterior)
    for hole in poly.interiors:
        connection_lines.extend(get_connection_lines(hole))
    fig, ax = plt.subplots()

    x, y = poly.exterior.xy
    ax.plot(x, y, color="black", linewidth=3)
    for hole in poly.interiors:
        x, y = hole.xy
        ax.plot(x, y, color="black", linewidth=3)
        
    for line in connection_lines:
        x, y = line.xy
        ax.plot(x, y, linewidth=5)
    ax.axis("equal")
    plt.show()