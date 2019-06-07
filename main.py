#!/usr/bin/env python3
from src.genpath import gen_square, centralize
from src.flow import flow_math, extrude
from src.gcode import output_gcode, gen_layer
from shapely.figures import SIZE, plot_bounds
import matplotlib.pyplot as plt
import numpy as np
import configparser

with open('assets/header.gcode', 'r') as f:
    header = f.readlines()
header = "".join(header)

with open('assets/footer.gcode', 'r') as f:
    footer = f.readlines()
footer = "".join(footer)

with open('assets/second.gcode', 'r') as f:
    second = f.readlines()
second_header = "".join(second)

with open('assets/splash.txt', 'r') as f:
    splash = f.readlines()
splash = "".join(splash)

config = configparser.ConfigParser()
config.read('config.ini')

length = float(config['DEFAULT']['length'])
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

print(splash.format(length,
                  gap,
                  width,
                  height,
                  angle0,
                  filament_d,
                  adjust * 100,
                  flow,
                  bed_x,
                  bed_y,
                  output_name))


path_a = gen_square(length, length, gap, angle0)
path_a = centralize(path_a, bed_x, bed_y)
x, y = path_a.xy
e = extrude(x, y, flow)

path_b = gen_square(length, length, gap, angle1, True, True)
print(path_b.length)
path_b = centralize(path_b, bed_x, bed_y)
x1, y1 = path_b.xy
e1 = extrude(x1, y1, flow)

layers = []
for i in range(100):
    if i%2:
        layers.append(gen_layer(x1, y1, height*(i+1), e1))
    else:
        layers.append(gen_layer(x, y, height*(i+1), e))

output_gcode(layers, output_name, date, header, footer)

fig = plt.figure(1, figsize=SIZE, dpi=90)

ax = fig.add_subplot(121)
x2, y2 = path_a.xy
ax.plot(x2, y2)
plot_bounds(ax, path_a)
ax.grid(True)
ax.set_title('A')
plt.axis('equal')

ax = fig.add_subplot(122)
x2, y2 = path_b.xy
ax.plot(x2, y2)
plot_bounds(ax, path_b)
ax.grid(True)
ax.set_title('B')
plt.axis('equal')

plt.show()
