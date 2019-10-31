#!/usr/bin/env python3
from src.flow import flow_math, extrude
from src.gcode import output_gcode, gen_layer2, parse_gcode
from src.plotpath import plot_layer
import src.layer as layer
import src.initconfig as cfg
from shapely import affinity
from itertools import cycle
from shapely.geometry import LineString

from shapely import affinity
from shapely.figures import SIZE, set_limits, plot_line, plot_bounds, color_issimple
from shapely.figures import plot_coords as _plot_coords
import matplotlib.pyplot as plt

fig = plt.figure(1, figsize=SIZE, dpi=90)
ax = fig.add_subplot(111)

flow = flow_math(cfg.width, cfg.height, cfg.filament_diameter, 1)
'''
shape = [(0,0), (20,0),(30,20), (10,20)]
skirt = layer.Layer(shape, 5, 4, 0.5, cfg.bed, 0)
a = layer.Layer(shape, -0.48/2, 5, 0.5, cfg.bed, 45)
b = layer.Layer(shape, -0.48/2, 5, 0.5, cfg.bed, -45)
skirt.translate((cfg.bed_x - a.bounds[0])/2, (cfg.bed_y - a.bounds[1])/2)
a.translate((cfg.bed_x - a.bounds[0])/2, (cfg.bed_y - a.bounds[1])/2)
b.translate((cfg.bed_x - b.bounds[0])/2, (cfg.bed_y - b.bounds[1])/2)
'''

L = 10
square = [(0, 0), (10, 0), (10, 0.5), (0, 0.5), (0, 1), (10, 1), (10, 1.5), (0, 1.5), (0, 2), (10, 2), (10, 2.5), (0, 2.5), (0, 3), (10, 3)]
rabeta = [(10, 3), (10+L, 3)]

sq = LineString(square)
rb = LineString(rabeta)

sq = affinity.translate(sq, 100, 100)
rb = affinity.translate(rb, 100, 100)


l = 5
pente = []
dente = []
for i in range(l):
    pente.append(affinity.translate(sq, 0, i*3))
    dente.append(affinity.translate(rb, 0, i*3))


layers = []

for j in range(3):
    for i in range(l):
        x, y = pente[i].xy
        e = extrude(x, y, flow)
        layers.append(gen_layer2(x, y, cfg.height * (j+1), e, cfg.vel))
        x, y = dente[i].xy
        e = extrude(x, y, flow*0)
        layers.append(gen_layer2(x, y, cfg.height * (j+1), e, cfg.vel))


output_gcode(layers, cfg.output_f, cfg.header, cfg.footer)


for i in range(l):
    plot_line(ax, pente[i])
    plot_line(ax, dente[i], color = 'red')
ax.grid(True)
plt.axis('equal')
plt.show()

'''
layers = []

for p in skirt.perimeters:
    x, y = p.xy
    e = extrude(x, y, flow)
    layers.append(gen_layer(x, y, cfg.height, e))

for i in range(16):
    for p in a.perimeters:
        x, y = p.xy
        e = extrude(x, y, flow)
        layers.append(gen_layer(x, y, cfg.height * (2*i+1), e))

    for p in a.inner_shape:
        x, y = p.xy
        e = extrude(x, y, flow)
        layers.append(gen_layer(x, y, cfg.height * (2*i+1), e))

    for p in b.perimeters:
        x, y = p.xy
        e = extrude(x, y, flow)
        layers.append(gen_layer(x, y, cfg.height * (2*i+2), e))
    for p in b.inner_shape:
        x, y = p.xy
        e = extrude(x, y, flow)
        layers.append(gen_layer(x, y, cfg.height * (2*i+2), e))

output_gcode(layers, cfg.output_f, cfg.header, cfg.footer)
plot_layer(b)
'''

#gcode_parsed, gcode_raw = parse_gcode('elefante.gcode')
#print(gcode_parsed[2])
