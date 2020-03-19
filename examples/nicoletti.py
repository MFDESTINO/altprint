#!/usr/bin/env python3

import matplotlib.pyplot as plt
from shapely.geometry import LineString, MultiLineString, GeometryCollection, Polygon
from shapely.ops import split
from shapely import affinity
from prynter.core import Layer
from prynter.path.rectilinear_fill import rectilinear_fill
from prynter.path.retract import retract
from prynter.plot import plot_layer
from prynter.flow import calculate, extrude
from prynter.gcode import gen_layer2, output_gcode, read_script
from prynter.imports import read_dxf
import os

flow_val = calculate()
model_file = "models/n25.dxf"
bounds = read_dxf(model_file, "0")
process1 = read_dxf(model_file, "process1")
process2 = read_dxf(model_file, "process2")
process3 = read_dxf(model_file, "process3")
process4 = read_dxf(model_file, "process4")

object_border = LineString(bounds)
process1_border = LineString(process1)
process1_zone = Polygon(process1)
process2_border = LineString(process2)
process2_zone = Polygon(process2)
process3_border = LineString(process3)
process3_zone = Polygon(process3)
process4_border = LineString(process4)
process4_zone = Polygon(process4)

layer_0 = Layer(border=object_border, perimeters_num=2)
layer_0.infill = rectilinear_fill(layer_0.inner_border, 0)
layer_n = Layer(border=object_border, perimeters_num=2)
layer_n.infill = rectilinear_fill(layer_n.inner_border, 0)

final = []
for i, infill in enumerate(layer_n.infill):
    for j in list(split(infill, process1_border)):
        final.append(j)
layer_n.infill = final

final = []
for i, infill in enumerate(layer_n.infill):
    for j in list(split(infill, process2_border)):
        final.append(j)
layer_n.infill = final

final = []
for i, infill in enumerate(layer_n.infill):
    for j in list(split(infill, process3_border)):
        final.append(j)
layer_n.infill = final

final = []
for i, infill in enumerate(layer_n.infill):
    for j in list(split(infill, process4_border)):
        final.append(j)
layer_n.infill = final

#layer_n.infill = list(split(layer_n.infill[0], process1_border))

ax = plt.subplot()
plot_layer(ax, layer_n)
layers = []
asd = False
asd2 = False
asd3 = False
for i in range(25):
    if i<2 or i>22:
        for perimeter in layer_0.perimeters:
            x, y = perimeter.xy
            e = extrude(x, y, flow_val*1.2)
            layers.append(gen_layer2(x, y, 0.2 * (i+1), e, 2100))
        for line in layer_0.infill:
            x, y = line.xy
            e = extrude(x, y, flow_val*1.2)
            layers.append(gen_layer2(x, y, 0.2 * (i+1), e, 2100))
    else:
        for perimeter in layer_n.perimeters:
            x, y = perimeter.xy
            e = extrude(x, y, flow_val)
            layers.append(gen_layer2(x, y, 0.2 * (i+1), e, 2100))

        for line in layer_n.infill:
            if line.within(process1_zone) or line.within(process2_zone) or line.within(process3_zone) or line.within(process4_zone):
                x, y = line.xy
                bridge, rec = retract(x, y, 0.1)
                e1 = extrude(bridge[0], bridge[1], flow_val*2)
                e2 = extrude(rec[0], rec[1], flow_val*1)
                if not asd:
                    ax.plot(bridge[0], bridge[1], linewidth=1, color='red', label="200%")
                    asd = True
                else:
                    ax.plot(bridge[0], bridge[1], linewidth=1, color='red')

                if not asd2:
                    ax.plot(rec[0], rec[1], linewidth=2, color='orange', label='100%')
                    asd2 = True
                else:
                    ax.plot(rec[0], rec[1], linewidth=2, color='orange')
                layers.append(gen_layer2(bridge[0], bridge[1], 0.2 * (i+1), e1, 2100))
                layers.append(gen_layer2(rec[0], rec[1], 0.2 * (i+1), e2, 2100))

            else:
                x, y = line.xy
                e = extrude(x, y, flow_val*0.7)
                layers.append(gen_layer2(x, y, 0.2 * (i+1), e, 2100))
                if not asd3:
                    ax.plot(x, y, linewidth=0.5, color='blue', label="60%")
                    asd3 = True
                else:
                    ax.plot(x, y, linewidth=0.5, color='blue')


START = read_script("scripts/start.gcode")
END = read_script("scripts/end.gcode")

output_gcode(layers, "n25", START, END)

ax.grid(True)
ax.legend(loc='lower right',fontsize='large')
plt.axis('equal')
plt.title("Corpo de prova - Caso 75%")
plt.show()
