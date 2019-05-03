#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import configparser

with open('src/header.gcode', 'r') as f:
    header = f.readlines()
header = "".join(header)

with open('src/footer.gcode', 'r') as f:
    footer = f.readlines()
footer = "".join(footer)

with open('src/second.gcode', 'r') as f:
    second = f.readlines()
second_header = "".join(second)

with open('src/splash', 'r') as f:
    splash = f.readlines()
splash = "".join(splash)

def plot_path(x, y):
    # Plota a trajetória, usando setas para indicar a direção
    # path: matriz de pontos da trajetória
    plt.plot(x, y)
    plt.axis('equal')
    '''for i in range(len(x) - 1):
        dx = x[i + 1] - x[i]
        dy = y[i + 1] - y[i]
        plt.arrow(x[i], y[i], dx, dy,
              shape='full',
              lw=0,
              length_includes_head=True,
              head_width=.1)'''
    plt.show()

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

def rotate(x, y, a):
    theta = np.radians(a)
    c, s = np.cos(theta), np.sin(theta)
    R = np.array(((c,-s), (s, c)))

    A = np.array((x, y))
    B = np.dot(R, A)
    return B

def cutbelow(x, y, a):
    theta = np.radians(a)
    b = np.tan(theta)
    for i in range(len(x)):
        ym = b*x[i]
        if y[i] < ym:
            y[i] = ym
    return (x, y)

def cutabove(x, y, a, l):
    theta = np.radians(a)
    b = np.tan(theta)
    c = l/np.cos(theta)
    for i in range(len(x)):
        ym = b*x[i] + c
        if y[i] > ym:
            y[i] = ym
    return (x, y)

def cuttest(x, y):
    for i in range(len(x)):
        ym = np.sqrt(16 - x[i]**2)
        if y[i] > ym:
            y[i] = ym
    return (x, y)

def remove_doubles(x, y, l):
    while x[0] < 0:
        x = np.delete(x, 0)
        y = np.delete(y, 0)
    while y[-1] < 0:
        x = np.delete(x, -1)
        y = np.delete(y, -1)
    return(x, y)


def extrude(x, y, flow):
    extrusion = np.zeros(len(x))
    for i in range(1, len(x)):
        dx = abs(x[i] - x[i - 1])
        dy = abs(y[i] - y[i - 1])
        extrusion[i] = np.sqrt((dx**2) + (dy**2)) * flow + extrusion[i-1]
    return extrusion

def flow_math(w, h, df, adjust):
    a = 4 * w * h + (np.pi - 4) * h**2
    b = np.pi * df**2
    flow = adjust * a / b
    return flow

def output_gcode(x, y, e, output_name):
    with open(output_name + '.gcode', 'w') as f:
        f.write(header)
        for i in range(len(x)):
            f.write('G1 X{:.5} Y{:.5} E{:.5}\n'.format(x[i], y[i], e[i]))
        f.write(footer)

def output2_gcode(x, y, e, output_name):
    with open(output_name + '.gcode', 'w') as f:
        f.write(second_header)
        for i in range(len(x)):
            f.write('G1 X{:.5} Y{:.5} E{:.5}\n'.format(x[i], y[i], e[i]))


config = configparser.ConfigParser()
config.read('config.ini')

length = float(config['DEFAULT']['length'])
gap = float(config['DEFAULT']['gap'])
width = float(config['DEFAULT']['width'])
height = float(config['DEFAULT']['height'])
filament_d = float(config['DEFAULT']['filament_d'])
adjust = float(config['DEFAULT']['adjust'])
bed_x = float(config['DEFAULT']['bed_x'])
bed_y = float(config['DEFAULT']['bed_x'])
output_name = config['DEFAULT']['output']

flow = flow_math(width, height, filament_d, adjust)

print(splash.format(length,
                  gap,
                  width,
                  height,
                  filament_d,
                  adjust * 100,
                  flow,
                  bed_x,
                  bed_y,
                  output_name))

x, y = gen_square(int(2*length / gap))
x, y = scale(x, y, gap, gap)
ang = 15

x, y = translate(x, y, -length, 0)
#x, y = cuttest(x, y)
x, y = cutbelow(x, y, ang)
x, y = cutbelow(x, y, ang+90)
x, y = cutabove(x, y, ang, length)
x, y = cutabove(x, y, ang+90, -length)
x, y = rotate(x, y, -ang)
x, y = remove_doubles(x, y, length)
segunda_camada = False

if segunda_camada:
    #x, y = rotate(x, y)
    x, y = scale(x, y, 1, -1)
    x, y = translate(x, y, length, length)
x, y = translate(x, y, (bed_x - length) / 2, (bed_y - length) / 2)

e = extrude(x, y, flow)
print(x)
print(y)
plot_path(x, y)
#if segunda_camada:
#output2_gcode(x, y, e, 'segunda')
#else:
output_gcode(x, y, e, output_name)
