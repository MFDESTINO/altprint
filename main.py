#!/usr/bin/env python3
from src.flow import flow_math, extrude
from src.gcode import output_gcode, gen_layer
from src.plotpath import plot_layer
import src.layer as layer
import src.initconfig as cfg
from shapely import affinity
from itertools import cycle

flow = flow_math(cfg.width, cfg.height, cfg.filament_diameter, 1)

shape = [(0,0), (20,0),(30,20), (10,20)]
skirt = layer.Layer(shape, 5, 4, 0.5, cfg.bed, 0)
a = layer.Layer(shape, -0.48/2, 5, 0.5, cfg.bed, 45)
b = layer.Layer(shape, -0.48/2, 5, 0.5, cfg.bed, -45)
skirt.translate((cfg.bed_x - a.bounds[0])/2, (cfg.bed_y - a.bounds[1])/2)
a.translate((cfg.bed_x - a.bounds[0])/2, (cfg.bed_y - a.bounds[1])/2)
b.translate((cfg.bed_x - b.bounds[0])/2, (cfg.bed_y - b.bounds[1])/2)

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
