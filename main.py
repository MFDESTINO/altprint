#!/usr/bin/env python3
from prynter import flow, gcode, genpath, plotpath, layer
from prynter import initconfig as cfg
from shapely import affinity
from shapely.geometry import LineString, LinearRing, Polygon
from shapely.ops import split
from shapely.figures import SIZE, set_limits, plot_line, plot_bounds, color_issimple
from shapely.figures import plot_coords as _plot_coords
import matplotlib.pyplot as plt

fig = plt.figure(1, figsize=SIZE, dpi=90)
ax = fig.add_subplot(111)

flow_val = flow.calculate()

L = 15
object_shape = [(0,0), (40 + L,0), (40 + L, 15), (0, 15)]
alt_zone = LineString([(20, 0), (20 + L, 0), (20 + L, 15), (20, 15), (20, 0)])

skirt = layer.Layer(object_shape, 4, out_adj=5)
a = layer.Layer(object_shape, 0, angle=90)
a2 = layer.Layer(object_shape, 0)

center_x = (cfg.bed[0] - a.bounds[0])/2
center_y = (cfg.bed[1] - a.bounds[1])/2

alt_zone = affinity.translate(alt_zone, center_x, center_y)
skirt.translate(center_x, center_y)
a2.translate(center_x, center_y)
a.translate(center_x, center_y)
alt_zonep = Polygon(alt_zone)

a.inner_shape = split(a.inner_shape, alt_zone)
a2.inner_shape = split(a2.inner_shape, alt_zone)

layers = []
for line in skirt.perimeters:
    x, y = line.xy
    e = flow.extrude(x, y, flow_val*1)
    ax.plot(x,y, linewidth=4, color='blue')
    layers.append(gcode.gen_layer2(x, y, 0.2, e, 3000))

for i in range(3):
    for line in a.inner_shape:
        x, y = line.xy
        if line.within(alt_zonep):
            #e = extrude(x, y, flow*0)
            f = 0.9
            A = [x[0], y[0]]
            B = [x[1], y[1]]
            C = [A[0] + f*(B[0]-A[0]), A[1] + f*(B[1]-A[1])]
            acx = [A[0], C[0]]
            acy = [A[1], C[1]]
            cbx = [C[0], B[0]]
            cby = [C[1], B[1]]
            e1 = flow.extrude(acx, acy, flow_val*0)
            e2 = flow.extrude(cbx, cby, flow_val*2)
            ax.plot(acx, acy, linewidth=3, color='blue')
            ax.plot(cbx, cby, linewidth=5, color='red')
            layers.append(gcode.gen_layer2(acx, acy, 0.2 * (i+1), e1, 3000))
            layers.append(gcode.gen_layer2(cbx, cby, 0.2 * (i+1), e2, 3000))
        else:
            e = flow.extrude(x, y, flow_val*1.2)
            ax.plot(x,y, linewidth=5, color='gray')
            layers.append(gcode.gen_layer2(x, y, 0.2 * (i+1), e, 3000))

gcode.output_gcode(layers, cfg.output_f, cfg.header, cfg.footer)

ax.grid(True)
plt.axis('equal')
plt.show()
