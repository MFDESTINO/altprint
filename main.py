#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import configparser

def plot_path(x, y):
    # Plota a trajetória, usando setas para indicar a direção
    # path: matriz de pontos da trajetória
    plt.plot(x, y, drawstyle='steps')
    for i in range(len(x) - 1):
        dx = x[i + 1] - x[i]
        dy = y[i + 1] - y[i]
        plt.arrow(x[i], y[i], dx, dy,
              shape='full',
              lw=0,
              length_includes_head=True,
              head_width=.3)

def gen_square(n):
    x = np.zeros(n * 2 + 2)
    y = np.zeros(n * 2 + 2)
    for i in range(n * 2 + 2):
        x[i] = (i / 2) - ((1 - (-1) ** i) / 4)
        y[i] = (i%4%3%2 * n) + ((i + 3)%4%3%2 * n)
    return (x, y)

def scale(x, y, a, b):
    return (x * a, y * b)

def translate(x, y, dx, dy):
    return (x + dx, y + dy)

def extrude(x, y, flow):
    extrusion = np.zeros(len(x))
    for i in range(1, len(x)):
        dx = abs(x[i] - x[i - 1])
        dy = abs(y[i] - y[i - 1])
        extrusion[i] = np.sqrt((dx**2) + (dy**2)) * flow + extrusion[i-1]
    return extrusion


def output_gcode(x, y, e, output_name):
    with open(output_name + '.gcode', 'w') as f:
        for i in range(len(x)):
            f.write('G1 X{:.5} Y{:.5} E{:.5}\n'.format(x[i], y[i], e[i]))


config = configparser.ConfigParser()
config.read('config.ini')

length = float(config['DEFAULT']['length'])
gap = float(config['DEFAULT']['gap'])
flow = float(config['DEFAULT']['flow'])
bed_x = float(config['DEFAULT']['bed_x'])
bed_y = float(config['DEFAULT']['bed_x'])
output_name = config['DEFAULT']['output']

text = '''
  ___           __  __     _    _
 / __| __ __ _ / _|/ _|___| |__| |___ _ _
 \__ \/ _/ _` |  _|  _/ _ \ / _` / -_) '_|
 |___/\__\__,_|_| |_| \___/_\__,_\___|_|

     3d printing path generator

     Square path
     Length: {} mm
     Gap : {} mm
     Flow multiplier: {} mm
     Bed size: {} mm x {} mm
     Output file: {}.gcode
'''
print(text.format(length, gap, flow, bed_x, bed_y, output_name))

x, y = gen_square(int(length / gap))
x, y = scale(x, y, gap, gap)
x, y = translate(x, y, (bed_x - length) / 2, (bed_y - length) / 2)
e = extrude(x, y, flow)

output_gcode(x, y, e, output_name)
