import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon, LinearRing, MultiLineString, Point, MultiPoint
from shapely.figures import SIZE, set_limits, plot_line, plot_bounds, color_issimple
from shapely.figures import plot_coords as _plot_coords
from shapely.ops import linemerge
from shapely import affinity

def plot_coords(ax, ob, color='gray'):
    for line in ob:
        _plot_coords(ax, line, color=color, zorder=3)

def plot_lines(ax, ob, color='gray'):
    for line in ob:
        plot_line(ax, line, color=color, zorder=2)

def gen_lines(mx, my, gap):
    lines = []
    for i in range(int(mx/gap) + 1):
        lines.append(LineString([[i*gap,0], [i*gap,my]]))
    multi_line = MultiLineString(lines)
    return multi_line

def connect(n, points):
    lines = []
    for i in range(int(n / 2)):
        lines.append(LineString([points[2 * i], points[2 * i + 1]]))
    print(lines[0].coords[0][0])
    lines = sorted(lines, key=lambda line: line.coords[0][0])
    multi_line = MultiLineString(lines)
    return multi_line

def refine(collection):
    refined = []
    for o in collection:
        if type(o) != Point:
            refined.append(Point(o.coords[0]))
            refined.append(Point(o.coords[-1]))
        else:
            refined.append(o)
    if refined[0].coords[0][0] != refined[1].coords[0][0]:
        refined.pop(0)
    multi_point = MultiPoint(refined)
    return multi_point


def union_path(lines):
    n = len(lines) - 1
    path = []
    for i in range(n):
        if i % 2:
            path.append(lines[i])
            path.append(LineString([lines[i].coords[0], lines[i+1].coords[0]]))
        else:
            path.append(lines[i])
            path.append(LineString([lines[i].coords[-1], lines[i+1].coords[-1]]))
    path.append(lines[-1])
    multi_line = MultiLineString(path)
    return multi_line

borders_coords = [(0,2), (2,0), (4,2), (4,3), (3,4), (2,3), (1,4), (0, 3)]
borders = LinearRing(borders_coords)


mline1 = gen_lines(int(borders.bounds[2]), borders.bounds[3], 0.3)
inter = mline1.intersection(borders)
new = refine(inter)
print(new)
lines = connect(len(new), new)
final = union_path(lines)
asd = linemerge(final)


fig = plt.figure(1, figsize=SIZE, dpi=90)
#borders
ax = fig.add_subplot(221)

x1, y1 = borders.xy
ax.plot(x1, y1)

ax.grid(True)
ax.set_title('a) borders')
plt.axis('equal')

#superposition
ax = fig.add_subplot(222)
plot_coords(ax, mline1)
plot_coords(ax, new, 'red')
plot_bounds(ax, mline1)
plot_lines(ax, mline1)

ax.plot(x1, y1)

ax.grid(True)
ax.set_title('b) superposition')
plt.axis('equal')

#lines
ax = fig.add_subplot(223)

plot_coords(ax, lines)
plot_bounds(ax, lines)
plot_lines(ax, lines, 'orange')
ax.plot(x1, y1)

ax.grid(True)
ax.set_title('c) lines')
plt.axis('equal')

#final
ax = fig.add_subplot(224)
#ax.plot(x1, y1)
x2, y2 = asd.xy
ax.plot(x2, y2)


ax.grid(True)
ax.set_title('d) final')
plt.axis('equal')

plt.show()
