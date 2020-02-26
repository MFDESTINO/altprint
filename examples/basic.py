import matplotlib.pyplot as plt
from shapely.geometry import LineString
from prynter.core import Layer
from prynter.path.rectilinear_fill import rectilinear_fill
from prynter.plot import plot_layer
from prynter.flow import calculate, extrude
from prynter.gcode import gen_layer2, output_gcode

flow_val = calculate()

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

output_gcode(layers, "teste", START, END)

ax = plt.subplot()
plot_layer(ax, layer_0)
ax.grid(True)
plt.axis('equal')
plt.show()
