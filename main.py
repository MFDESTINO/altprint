#!/usr/bin/env python3
from src.gcode import output_gcode, gen_layer2, parse_gcode
from src.plotpath import plot_layer
import src.initconfig as cfg
import construct


printable_mesh = construct.build()
gcode_layers = []

for layer in printable_mesh:
    for movement in layer:
        gcode_layers.append(gen_layer(movement))

output_gcode(gcode_layers, cfg.output_f, cfg.header, cfg.footer)
