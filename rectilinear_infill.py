from shapely.geometry import LineString, Polygon, MultiPoint
import numpy as np
import matplotlib.pyplot as plt

shape = Polygon([(0,0), (10,0), (10, 10), (0, 10)])

border = [(0, 0), (10, 0), (10, 10), (20, 10), (20, 5), (30, 5), (30, 40), (10,25), (0, 30)]
holes = [[(5, 15), (15, 15), (15, 20), (5, 20)], [(20, 25), (25, 25), (25, 30)]]
shape = Polygon(border, holes)

gap = 3
thres = 0

# y = m*x+c
# x = (y-c)/m
# m = (y-y0)/(x-x0)
# c = y-m*x

def x_from_y(a, b, yc):
    dx = b[0]-a[0]
    dy = b[1]-a[1]
    if dx==0:
        return np.ones(len(yc))*a[0]
    return (yc - a[1])*dx/dy + a[0]


coords = shape.exterior.coords
points = []
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
    points.extend(list(zip(xs, ys)))

mp = MultiPoint(points)



fig, ax = plt.subplots()

x, y = shape.exterior.xy
ax.plot(x, y, color="gray")

for point in mp.geoms:
    x, y = point.xy
    ax.scatter(x, y)
ax.axis("equal")
plt.show()