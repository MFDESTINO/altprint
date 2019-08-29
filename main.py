#!/usr/bin/env python3
from src.genpath import gen_square, centralize, contour
from src.flow import flow_math, extrude
from src.gcode import output_gcode, gen_layer
from src.plotpath import plot_lines, plot_coords, plot_layer
from shapely.figures import SIZE, plot_bounds
import matplotlib.pyplot as plt
import numpy as np
import configparser

from shapely.geometry import LineString, LinearRing, MultiLineString, Point, MultiPoint, Polygon
from shapely import affinity

class Layer:
    def __init__(self, shape, out_adj, perimeters_num, gap, bed, angle):
        self.perimeters = []
        self.inner_shape = []
        self.shape = contour(shape, out_adj)
        self.out_adj = out_adj
        self.perimeters_num = perimeters_num
        self.gap = gap
        self.angle = angle
        self.inner_shape = gen_square(contour(self.shape,
            - self.gap * self.perimeters_num), self.gap, self.angle)

        for i in range(self.perimeters_num):
            self.perimeters.append(LinearRing(contour(self.shape, - self.gap * i)))

        self.perimeters = MultiLineString(self.perimeters)
        self.bounds = [self.perimeters.bounds[2] - self.perimeters.bounds[0],
                       self.perimeters.bounds[3] - self.perimeters.bounds[1]]

    def translate(self, dx, dy):
        self.inner_shape = affinity.translate(self.inner_shape, dx, dy)
        self.perimeters = affinity.translate(self.perimeters, dx, dy)



with open('assets/header.gcode', 'r') as f:
    header = f.readlines()
header = "".join(header)

with open('assets/footer.gcode', 'r') as f:
    footer = f.readlines()
footer = "".join(footer)

with open('assets/splash.txt', 'r') as f:
    splash = f.readlines()
splash = "".join(splash)

config = configparser.ConfigParser()
config.read('config.ini')

size_x = float(config['DEFAULT']['size_x'])
size_y = float(config['DEFAULT']['size_y'])
gap = float(config['DEFAULT']['gap'])
width = float(config['DEFAULT']['width'])
height = float(config['DEFAULT']['height'])
angle0 = float(config['DEFAULT']['angle0'])
angle1 = float(config['DEFAULT']['angle1'])
filament_d = float(config['DEFAULT']['filament_diameter'])
adjust = float(config['DEFAULT']['adjust'])
bed_x = float(config['DEFAULT']['bed_x'])
bed_y = float(config['DEFAULT']['bed_y'])
output_name = config['DEFAULT']['output']
date = config['DEFAULT']['date']
output_name = date + '-' + output_name

flow = flow_math(width, height, filament_d, adjust)

print(splash.format(size_x,
                  gap,
                  width,
                  height,
                  angle0,
                  angle1,
                  filament_d,
                  adjust * 100,
                  flow,
                  bed_x,
                  bed_y,
                  output_name))

bed = [bed_x, bed_y]

shape = [(0,0), (20,0),(30,20), (10,20)]
skirt = Layer(shape, 5, 4, 0.5, bed, 0)
a = Layer(shape, -0.48/2, 5, 0.5, bed, 45)
b = Layer(shape, -0.48/2, 5, 0.5, bed, -45)
skirt.translate((bed_x - a.bounds[0])/2, (bed_y - a.bounds[1])/2)
a.translate((bed_x - a.bounds[0])/2, (bed_y - a.bounds[1])/2)
b.translate((bed_x - b.bounds[0])/2, (bed_y - b.bounds[1])/2)

layers = []

for p in skirt.perimeters:
    x, y = p.xy
    e = extrude(x, y, flow)
    layers.append(gen_layer(x, y, 0.2, e))

for i in range(16):
    for p in a.perimeters:
        x, y = p.xy
        e = extrude(x, y, flow)
        layers.append(gen_layer(x, y, 0.2 * (2*i+1), e))
    x, y = a.inner_shape.xy
    e = extrude(x, y, flow)
    layers.append(gen_layer(x, y, 0.2 * (2*i+1), e))

    for p in b.perimeters:
        x, y = p.xy
        e = extrude(x, y, flow)
        layers.append(gen_layer(x, y, 0.2 * (2*i+2), e))
    x, y = b.inner_shape.xy
    e = extrude(x, y, flow)
    layers.append(gen_layer(x, y, 0.2 * (2*i+2), e))



output_gcode(layers, output_name, date, header, footer)

plot_layer(b)
