#!/usr/bin/env python3

##### test
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon
#####

from prynter.core import Layer
from prynter.path.rectilinear_fill import rectilinear_fill
from prynter.path.lineutil import retract, split_lines
from prynter.flow import calculate, extrude
from prynter.gcode import segment, jump, segment_to_gcode, read_script, output_gcode

border = LineString([(0,0), (50,0), (50, 10), (0, 10),  (0,0)])
area1 = Polygon([(20,-1), (30,-1), (30,11), (20,11), (20,-1)])

layer_0 = Layer(border=border)
layer_0.infill = rectilinear_fill(Polygon(layer_0.inner_border), 0.5)
layer_0.perimeters = split_lines(layer_0.perimeters, LineString(area1.exterior))
layer_0.infill = split_lines(layer_0.infill, LineString(area1.exterior))

flow = calculate()
layers = []
x0, y0 = 0, 0
v = 2400
START = read_script("scripts/start.gcode")
END = read_script("scripts/end.gcode")
regions = [(area1, 0)]

for i in range(10):
    z = 0.2 * (i+1)
    for line in layer_0.perimeters:
        l, x0, y0 = segment_to_gcode(line, regions, flow, 0.2 * (i+1), v, x0, y0)
        layers.extend(l)
    for line in layer_0.infill:
        l, x0, y0 = segment_to_gcode(line, regions, flow, 0.2 * (i+1), v, x0, y0)
        layers.extend(l)


output_gcode(layers, "test", START, END)

ax = plt.subplot()

for line in layer_0.perimeters:
    x, y = line.xy
    ax.plot(x, y)

for line in layer_0.infill:
    x, y = line.xy
    ax.plot(x, y)

x, y = area1.exterior.xy
ax.plot(x, y, color="red")

ax.grid(True)
plt.axis('equal')
plt.show()
