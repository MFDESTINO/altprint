#!/usr/bin/env python3
import prynter
from prynter import flow, gcode, genpath, layer
from shapely import affinity
from shapely.geometry import LineString, LinearRing, Polygon
from shapely.ops import split
from shapely.figures import SIZE
import matplotlib.pyplot as plt

flow_val = flow.calculate()
L = 15
FNAME = prynter.output_f
START = '''G90
M82
M106 S0
M104 S238 T0
M109 S238 T0
M140 S110
G28
G1 Z5 F1000
G32 S1
T0
M102
M106 S255
G92 E0.0000
G1 E-1.0000 F2400
M103
M101'''

END = '''
M103
; layer end
106 S0 ; Turn off fan
M104 S0 ; turn off extruder
M140 S0 ; turn off bed
G1 X0 Y210 F4000 ; move head away from part
M84 ; turn off motors
'''

object_shape = [(0,0), (40 + L,0), (40 + L, 15), (0, 15)]
for i in range(len(object_shape)):
    object_shape[i] = (object_shape[i][0]+10, object_shape[i][1]+10)

alt_zone = LineString([(20, -1), (20 + L, -1), (20 + L, 16), (20, 16), (20, -1)])
alt_zone = affinity.translate(alt_zone, 10, 10)

skirt = layer.Layer(object_shape, 4, out_adj=5)
a = layer.Layer(object_shape, 0, angle=90)
a2 = layer.Layer(object_shape, 0)

alt_zonep = Polygon(alt_zone)

a.inner_shape = split(a.inner_shape, alt_zone)
a2.inner_shape = split(a2.inner_shape, alt_zone)

fig = plt.figure(1, figsize=SIZE, dpi=90)
ax = fig.add_subplot(111)

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
            bridge, rec = genpath.retract(x, y, 0.9)
            e1 = flow.extrude(bridge[0], bridge[1], flow_val*0)
            e2 = flow.extrude(rec[0], rec[1], flow_val*2)
            ax.plot(bridge[0], bridge[1], linewidth=3, color='blue')
            ax.plot(rec[0], rec[1], linewidth=5, color='red')
            layers.append(gcode.gen_layer2(bridge[0], bridge[1], 0.2 * (i+1), e1, 3000))
            layers.append(gcode.gen_layer2(rec[0], rec[1], 0.2 * (i+1), e2, 3000))
        else:
            e = flow.extrude(x, y, flow_val*1.2)
            ax.plot(x,y, linewidth=5, color='gray')
            layers.append(gcode.gen_layer2(x, y, 0.2 * (i+1), e, 3000))

gcode.output_gcode(layers, FNAME, START, END)

ax.grid(True)
plt.axis('equal')
plt.show()
