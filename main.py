#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np

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

def gen_square_path(n):
    # cria uma trajetória quadrangular
    # n: dimensao externa do quadrado, em u.a.
    # retorna uma matriz com pontos (x,y) da trajetoria
    # Como o espaço entre as linhas é de uma u.a., o número de movimentos
    # feitos é de 2n + 2
    x = np.zeros(n * 2 + 2)
    y = np.zeros(n * 2 + 2)
    for i in range(n * 2 + 2):
        if i % 2:
            y[i] = n - y[i - 1]
            x[i] = x[i - 1]
        else:
            x[i] = i / 2
            y[i] = y[i - 1]
    return [x, y]

def rotate(path):
    # Rotaciona em 90 graus antihorário a trajetória
    # path: matriz de pontos da trajetória
    # T(x,y) = (a - y, x)
    n = int((len(path[0]) - 2) / 2)
    a = np.ones(len(path[1])) * n
    return [a - path[1], path[0]]

def mirror(path):
    # Inverte a trajetória
    # path: matriz de pontos da trajetória
    # T(x,y) = (x, a - y)
    n = int((len(path[0]) - 2) / 2)
    a = np.ones(len(path[1])) * n
    return [path[0], a - path[1]]

asd = gen_square_path(4)
fgh = mirror(rotate(asd))

plot_path(asd)
#plot_path(fgh)
plt.show()
