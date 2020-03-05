#!/usr/bin/env python3

import matplotlib.pyplot as plt
from shapely.geometry import LineString
from prynter.core import Layer
from prynter.path.rectilinear_fill import rectilinear_fill
from prynter.plot import plot_layer
from prynter.flow import calculate, extrude
from prynter.gcode import gen_layer2, output_gcode, read_script

flow_val = calculate()


object_border = LineString([(0,0), (10,0), (10,10), (5, 10), (0, 0)])
layer_0 = Layer(border=object_border, perimeters_num=3)
layer_0.infill = rectilinear_fill(layer_0.inner_border, 45)
layer_0.translate(100, 100)

layers = []
for i in range(10):
    for perimeter in layer_0.perimeters:
        x, y = perimeter.xy
        e = extrude(x, y, flow_val)
        layers.append(gen_layer2(x, y, 0.2 * (i+1), e, 3000))
    for line in layer_0.infill:
        x, y = line.xy
        e = extrude(x, y, flow_val)
        layers.append(gen_layer2(x, y, 0.2 * (i+1), e, 3000))


START = read_script("scripts/start.gcode")
END = read_script("scripts/end.gcode")

output_gcode(layers, "teste", START, END)

ax = plt.subplot()
plot_layer(ax, layer_0)
ax.grid(True)
plt.axis('equal')
plt.show()
