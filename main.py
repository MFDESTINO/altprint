#!/usr/bin/env python3
from src.genpath import gen_square, centralize, contour
from src.flow import flow_math, extrude
from src.gcode import output_gcode, gen_layer
from src.plotpath import plot_lines, plot_coords
from shapely.figures import SIZE, plot_bounds
import matplotlib.pyplot as plt
import numpy as np
import configparser

from shapely.geometry import LineString, LinearRing, MultiLineString, Point, MultiPoint, Polygon
from shapely import affinity

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



shape = [(0,0), (20,0), (40, 20), (20,20)]
square = []
square2 = []
shape_adj = contour(shape, -0.24)
shape_i = contour(shape_adj, -2.5)

L = -0.5
for i in range(5):
    square.append(LinearRing(contour(shape_adj, L*i)))
    print(square[i].bounds[0])
sq = LinearRing(contour(shape_adj, -2.5))
path_i = gen_square(shape_i, 0.5, 90)
path_i = affinity.translate(path_i, sq.bounds[0], sq.bounds[1])
square.append(path_i)
path_c = MultiLineString(square)
#path_c = centralize(path_c, bed_x, bed_y)

for i in range(5):
    square2.append(LinearRing(contour(shape_adj, L*i)))
path_i = gen_square(shape_i, 0.5, -45)
path_i = affinity.translate(path_i, 7, 2.75)
square2.append(path_i)
path_c2 = MultiLineString(square2)
#path_c2 = centralize(path_c2, bed_x, bed_y)


layers = []
for i in range(16):
    for j in range(len(path_c)):
        x, y = path_c[j].xy
        e = extrude(x, y, flow)
        layers.append(gen_layer(x, y, 0.2 * ((2*i)+1), e))
    for j in range(len(path_c2)):
        x, y = path_c2[j].xy
        e = extrude(x, y, flow)
        layers.append(gen_layer(x, y, 0.2 * ((2*i)+2), e))



output_gcode(layers, output_name, date, header, footer)

fig = plt.figure(1, figsize=SIZE, dpi=90)

ax = fig.add_subplot(111)

for l in path_c:
    x, y = l.xy
    ax.plot(x,y)
ax.grid(True)
ax.set_title('A')
plt.axis('equal')


plt.show()
