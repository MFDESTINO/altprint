#!/usr/bin/env python3

import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon
from shapely.affinity import translate
from prynter.core import Layer
from prynter.path.rectilinear_fill import rectilinear_fill
from prynter.path.lineutil import retract, split_lines
from prynter.plot import plot_layer
from prynter.flow import calculate, extrude
from prynter.gcode import segment, jump, output_gcode, read_script
from prynter.imports import read_dxf

model_file = "models/snap2.dxf"

shape_border  = read_dxf(model_file, "base")
skirt_border = read_dxf(model_file, "skirt")
area1 = Polygon(read_dxf(model_file, "area3a"))
area2 = Polygon(read_dxf(model_file, "area3b"))

layer_0 = Layer(border=shape_border , perimeters_num=2)
skirt = Layer(border=skirt_border, perimeters_num=0, skirt_num=[2, 0])
layer_0.infill = rectilinear_fill(Polygon(layer_0.inner_border), 0.5)

layer_0.infill = split_lines(layer_0.infill, LineString(area1.exterior))
layer_0.perimeters = split_lines(layer_0.perimeters, LineString(area1.exterior))
layer_0.infill = split_lines(layer_0.infill, LineString(area2.exterior))
layer_0.perimeters = split_lines(layer_0.perimeters, LineString(area2.exterior))



first_layer_height = 0.2
v0 = 1200
v1 = 2100

ax = plt.subplot()
ax.grid(True)
x0, y0 = 0, 0
layers = []
flow_val = calculate()

def segment_to_gcode(line, regions, default_flow, z, v, x0, y0):
    layers = []
    for region, flow in regions:
        if line.within(region):
            x, y = line.xy
            acx, acy, cbx, cby = retract(x, y, 0.9)
            if LineString([(x0, y0), (x[0], y[0])]).length > 1:
                layers.append(jump(x[0], y[0]))
            x0, y0 = x[-1], y[-1]
            e1 = extrude(acx, acy, default_flow*flow)
            layers.append(segment(acx, acy, z, e1, v))
            e2 = extrude(cbx, cby, default_flow*2)
            layers.append(segment(cbx, cby, z, e2, v))
            return layers, x0, y0
    x, y = line.xy
    if LineString([(x0, y0), (x[0], y[0])]).length > 1:
        layers.append(jump(x[0], y[0]))
    x0, y0 = x[-1], y[-1]
    e = extrude(x, y, default_flow)
    layers.append(segment(x, y, z, e, v))
    return layers, x0, y0

regions = [(area1, 0), (area2, 0)]

for i in range(10):
    for line in layer_0.perimeters:
        l, x0, y0 = segment_to_gcode(line, regions, flow_val, 0.2 * (1+i), v0, x0, y0)
        layers.extend(l)

    for j, line in enumerate(layer_0.infill):
        l, x0, y0 = segment_to_gcode(line, regions, flow_val, 0.2 * (1+i), v0, x0, y0)
        layers.extend(l)

START = read_script("scripts/start.gcode")
END = read_script("scripts/end.gcode")

output_gcode(layers, "snapfit_macho_s2_a3_v3", START, END)
x, y = layer_0.inner_border.xy
#ax.plot(x, y, color="red", linewidth=2)
plt.axis('equal')
#plt.show()
