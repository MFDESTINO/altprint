#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import configparser
import math

def plot_path(path):
    # Plota a trajetória, usando setas para indicar a direção
    # path: matriz de pontos da trajetória
    plt.plot(path[0], path[1], drawstyle='steps')
    for i in range(len(path[0]) - 1):
        x = path[0][i]
        y = path[1][i]
        dx = path[0][i + 1] - x
        dy = path[1][i + 1] - y
        plt.arrow(x, y, dx, dy,
              shape='full',
              lw=0,
              length_includes_head=True,
              head_width=.3)

def gen_square_path(l, a):
    # cria uma trajetória quadrangular
    # n: dimensao externa do quadrado, em u.a.
    # retorna uma matriz com pontos (x,y) da trajetoria
    # Como o espaço entre as linhas é de uma u.a., o número de movimentos
    # feitos é de 2n + 2

    n = int(l/a)
    x = np.zeros(n * 2 + 2)
    y = np.zeros(n * 2 + 2)
    for i in range(n * 2 + 2):
        if i % 2:
            y[i] = n - y[i - 1]
            x[i] = x[i - 1]
        else:
            x[i] = i / 2
            y[i] = y[i - 1]
    path = np.array((x, y)) * a
    return path

def rotate(path, l):
    # Rotaciona em 90 graus antihorário a trajetória
    # path: matriz de pontos da trajetória
    # T(x,y) = (a - y, x)
    a = np.full(len(path[1]), l)
    return np.array((a - path[1], path[0]))

def mirror(path,  l):
    # Inverte a trajetória
    # path: matriz de pontos da trajetória
    # T(x,y) = (x, a - y)
    a = np.full(len(path[1]), l)
    return np.array((path[0], a - path[1]))

def delta(a, b, i):
    x = a[i]
    y = b[i]
    if(i > 0):
        dx = abs(x - a[i-1])
        dy = abs(y - b[i-1])
    else:
        dx = 0
        dy = 0
    return math.sqrt((dx**2) + (dy**2)) * 0.4

def output_gcode(path):
    with open('output.gcode', 'w') as f:
        e = 0
        for i in range(len(path[0])):
            e += delta(path[0], path[1], i)
            f.write('G1 X{:.5} Y{:.5} E{:.5}\n'.format(path[0][i] + 50, path[1][i] + 50, e ))


config = configparser.ConfigParser()
config.read('config.ini')

l = float(config['DEFAULT']['length'])
a = float(config['DEFAULT']['gap'])

asd = gen_square_path(l, a)
fgh = mirror(rotate(asd, l), l)
output_gcode(asd)
