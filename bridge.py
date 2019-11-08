from src.flow import flow_math, extrude
from src.gcode import output_gcode, gen_layer2, parse_gcode
from src.plotpath import plot_layer
import src.layer as layer
import src.initconfig as cfg
from shapely import affinity
from itertools import cycle
from shapely.geometry import LineString, LinearRing, Polygon
from shapely.ops import split

from shapely import affinity
from shapely.figures import SIZE, set_limits, plot_line, plot_bounds, color_issimple
from shapely.figures import plot_coords as _plot_coords
import matplotlib.pyplot as plt

fig = plt.figure(1, figsize=SIZE, dpi=90)
ax = fig.add_subplot(111)

flow = flow_math(cfg.width, cfg.height, cfg.filament_diameter, 1)
layers = []
L = 15
shape = [(0,0), (40 + L,0), (40 + L, 15), (0, 15)]
zone = [(20, 0), (20 + L, 0), (20 + L, 15), (20, 15), (20, 0)]
zone = LineString(zone)
skirt = layer.Layer(shape, 5, 4, 0.5, 0)
a = layer.Layer(shape, -0.48/2, 0, 0.5, 90)
a2 = layer.Layer(shape, -0.48/2, 0, 0.5, 0)
zone = affinity.translate(zone, (cfg.bed[0] - a.bounds[0])/2, (cfg.bed[1] - a.bounds[1])/2)
skirt.translate((cfg.bed[0] - a.bounds[0])/2, (cfg.bed[1] - a.bounds[1])/2)
a2.translate((cfg.bed[0] - a.bounds[0])/2, (cfg.bed[1] - a.bounds[1])/2)
a.translate((cfg.bed[0] - a.bounds[0])/2, (cfg.bed[1] - a.bounds[1])/2)
zonep = Polygon(zone)

a.inner_shape = split(a.inner_shape, zone)
a2.inner_shape = split(a2.inner_shape, zone)

for line in skirt.perimeters:
    x, y = line.xy
    e = extrude(x, y, flow*1)
    ax.plot(x,y, linewidth=4, color='blue')
    layers.append(gen_layer2(x, y, 0.2, e, 3000))

for i in range(3):
    for line in a.inner_shape:
        x, y = line.xy
        if line.within(zonep):
            #e = extrude(x, y, flow*0)
            f = 0.9
            A = [x[0], y[0]]
            B = [x[1], y[1]]
            C = [A[0] + f*(B[0]-A[0]), A[1] + f*(B[1]-A[1])]
            acx = [A[0], C[0]]
            acy = [A[1], C[1]]
            cbx = [C[0], B[0]]
            cby = [C[1], B[1]]
            e1 = extrude(acx, acy, flow*0)
            e2 = extrude(cbx, cby, flow*2)
            ax.plot(acx, acy, linewidth=3, color='blue')
            ax.plot(cbx, cby, linewidth=5, color='red')
            layers.append(gen_layer2(acx, acy, 0.2 * (i+1), e1, 3000))
            layers.append(gen_layer2(cbx, cby, 0.2 * (i+1), e2, 3000))
        else:
            e = extrude(x, y, flow*1.2)
            ax.plot(x,y, linewidth=5, color='gray')
            layers.append(gen_layer2(x, y, 0.2 * (i+1), e, 3000))

output_gcode(layers, cfg.output_f, cfg.header, cfg.footer)

ax.grid(True)
plt.axis('equal')
plt.show()
