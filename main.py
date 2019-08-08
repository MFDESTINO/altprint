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



shape = [(0,0), (10,0), (10, 10), (0,10)]
square = LinearRing(shape)


L = -0.4
testlines = []
square_border = LinearRing(contour(shape, L))

fig = plt.figure(1, figsize=SIZE, dpi=90)

ax = fig.add_subplot(111)
x, y = square.xy
ax.plot(x,y)
x2, y2 = square_border.xy
ax.plot(x2, y2)
ax.grid(True)
ax.set_title('A')
plt.axis('equal')


plt.show()
