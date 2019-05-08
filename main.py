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
    """
    Plota a trajetória.

    Args:
    x: vetor com as componentes x dos pontos
    y: vetor com as componentes y dos pontos
    """
    plt.plot(x, y)
    plt.axis('equal')
    plt.show()

def gen_square(n):
    """
    Gera uma trajetória quadrada com n gaps. Cada gap tem dimensão unitária.
    O tamanho dos vetores x e y é a quantidade e movimentos necessários, 2n+2.

    Args:
    n: número de gaps da trajetória quadrada.

    Returns:
    (x, y): tupla contendo os vetores das componentes x e y dos pontos
    """
    x = np.zeros(n * 2 + 2)
    y = np.zeros(n * 2 + 2)
    for i in range(n * 2 + 2):
        x[i] = (i / 2) - ((1 - (-1) ** i) / 4) #aqui vão duas séries numéricas
        y[i] = (i%4%3%2 * n) + ((i + 3)%4%3%2 * n) #um pouco complicado
    return (x, y)

def scale(x, y, a, b):
    """
    Altera a escala da trajetória.

    Args:
    x: vetor com as componentes x dos pontos
    y: vetor com as componentes y dos pontos
    a: fator de escala em x
    b: fator de escala em y

    Returns:
    (x, y): tupla contendo os vetores das componentes x e y dos pontos
    """
    return (x * a, y * b)

def translate(x, y, dx, dy):
    """
    Translaciona a trajetória.

    Args:
    x: vetor com as componentes x dos pontos
    y: vetor com as componentes y dos pontos
    dx: deslocamento em x
    dy: deslocamento em y

    Returns:
    (x, y): tupla contendo os vetores das componentes x e y dos pontos
    """
    return (x + dx, y + dy)

def rotate(x, y, a):
    """
    Aplica uma rotação no sentido antihorário nos pontos, usando uma matriz rotação.

    Args:
    x: vetor com as componentes x dos pontos
    y: vetor com as componentes y dos pontos
    a: ângulo em graus

    Returns:
    (x, y): tupla contendo os vetores das componentes x e y dos pontos
    """
    theta = np.radians(a)
    c, s = np.cos(theta), np.sin(theta)
    R = np.array(((c,-s), (s, c)))

    A = np.array((x, y))
    B = np.dot(R, A)
    return B

def cutbelow(x, y, a):
    """
    Aplica um corte na trajetória, usando uma reta centrada na origem,
    movendo todos os pontos para cima da reta.

    Args:
    x: vetor com as componentes x dos pontos
    y: vetor com as componentes y dos pontos
    a: ângulo em graus da reta.

    Returns:
    (x, y): tupla contendo os vetores das componentes x e y dos pontos
    """
    theta = np.radians(a)
    b = np.tan(theta)
    for i in range(len(x)):
        ym = b*x[i]
        if y[i] < ym:
            y[i] = ym
    return (x, y)

def cutabove(x, y, a, l):
    """
    Aplica um corte na trajetória, usando uma reta centrada na origem,
    movendo todos os pontos para baixo da reta.

    Args:
    x: vetor com as componentes x dos pontos
    y: vetor com as componentes y dos pontos
    a: ângulo em graus da reta.
    l: fator de deslocamento da reta em y

    Returns:
    (x, y): tupla contendo os vetores das componentes x e y dos pontos
    """
    theta = np.radians(a)
    b = np.tan(theta)
    c = l/np.cos(theta)
    for i in range(len(x)):
        ym = b*x[i] + c
        if y[i] > ym:
            y[i] = ym
    return (x, y)

def remove_doubles(x, y):
    """
    Remove todos os pontos fora do primeiro quadrante.

    Args:
    x: vetor com as componentes x dos pontos
    y: vetor com as componentes y dos pontos

    Returns:
    (x, y): tupla contendo os vetores das componentes x e y dos pontos
    """
    while x[0] < 0:
        x = np.delete(x, 0)
        y = np.delete(y, 0)
    while y[-1] < 0:
        x = np.delete(x, -1)
        y = np.delete(y, -1)
    return(x, y)


def extrude(x, y, flow):
    """
    Gera o vetor com as coordenadas da extrusão do filamento.

    Args:
    x: vetor com as componentes x dos pontos
    y: vetor com as componentes y dos pontos
    flow: fator multiplicador do fluxo

    Returns:
    extrusion: vetor com as coordenadas da extrusão do filamento.
    """
    extrusion = np.zeros(len(x))
    for i in range(1, len(x)):
        dx = abs(x[i] - x[i - 1])
        dy = abs(y[i] - y[i - 1])
        extrusion[i] = np.sqrt((dx**2) + (dy**2)) * flow + extrusion[i-1]
    return extrusion

def flow_math(w, h, df, adjust):
    """
    Calcula o fator multiplicador de fluxo de filamento, usandfo o modelo
    do retângulo com bordas circulares.

    Args:
    w: comprimento do raster
    h: altura do raster
    df: diametro do filamento
    adjust: fator de calibração

    Returns:
    flow: fator multiplicador do fluxo
    """
    a = 4 * w * h + (np.pi - 4) * h**2
    b = np.pi * df**2
    flow = adjust * a / b
    return flow

def output_gcode(x, y, e, output_name, header, footer):
    """
    Gera o arquivo gcode final.

    Args:
    x: vetor com as componentes x dos pontos
    y: vetor com as componentes y dos pontos
    e: vetor com as coordenadas da extrusão do filamento.
    output_name: nome do arquivo de saída
    header: cabeçalho do arquivo de saída
    footer: rodapé do arquivo de saída

    """
    with open(output_name + '.gcode', 'w') as f:
        f.write(header)
        for i in range(len(x)):
            f.write('G1 X{:.5} Y{:.5} E{:.5}\n'.format(x[i], y[i], e[i]))
        f.write(footer)

config = configparser.ConfigParser()
config.read('config.ini')

length = float(config['DEFAULT']['length'])
gap = float(config['DEFAULT']['gap'])
width = float(config['DEFAULT']['width'])
height = float(config['DEFAULT']['height'])
angle = float(config['DEFAULT']['angle'])
filament_d = float(config['DEFAULT']['filament_diameter'])
adjust = float(config['DEFAULT']['adjust'])
bed_x = float(config['DEFAULT']['bed_x'])
bed_y = float(config['DEFAULT']['bed_y'])
output_name = config['DEFAULT']['output']

flow = flow_math(width, height, filament_d, adjust)

print(splash.format(length,
                  gap,
                  width,
                  height,
                  angle,
                  filament_d,
                  adjust * 100,
                  flow,
                  bed_x,
                  bed_y,
                  output_name))

x, y = gen_square(int(2*length / gap))
x, y = scale(x, y, gap, gap)

#se o angulo for diferente de 0, aplica as transformações necessárias
if angle != 0:
    x, y = translate(x, y, -length, 0)
    x, y = cutbelow(x, y, angle)
    x, y = cutbelow(x, y, angle+90)
    x, y = cutabove(x, y, angle, length)
    x, y = cutabove(x, y, angle+90, -length)
    x, y = rotate(x, y, -angle)
    x, y = remove_doubles(x, y)

#Alinha a peça no centro da mesa
x, y = translate(x, y, (bed_x - length) / 2, (bed_y - length) / 2)
e = extrude(x, y, flow)

plot_path(x, y)
output_gcode(x, y, e, output_name, header, footer)
