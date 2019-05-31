import matplotlib.pyplot as plt
from genpath import gen_lines, connect, refine, union_path, gen_square, centralize
from shapely.figures import SIZE, plot_bounds
from flow import flow_math, extrude
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

def gen_layer(x, y, z, e):
    layer = []
    layer.append('G92 E0.0000\n')
    layer.append('M106 S255\n')
    layer.append('G1 X{0:.3f} Y{1:.3f} Z{2:.3f} F588\n'.format(x[0], y[0], z))
    for i in range(len(x)):
        layer.append('G1 X{0:.3f} Y{1:.3f} E{2:.4f}\n'.format(x[i], y[i], e[i]))
    layer = "".join(layer)
    return layer

def output_gcode(layers, output_name, header, footer):
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
        for layer in layers:
            f.write(layer)
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
date = config['DEFAULT']['date']
output_name = date + '-' + output_name

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


path_a = gen_square(length, length, gap, angle)
path_a = centralize(path_a, bed_x, bed_y)
x, y = path_a.xy
e = extrude(x, y, flow)

path_b = gen_square(length, length, gap, -angle)
path_b = centralize(path_b, bed_x, bed_y)
x1, y1 = path_b.xy
e1 = extrude(x1, y1, flow)

layers = []
for i in range(10):
    if i%2:
        layers.append(gen_layer(x1, y1, height*(i+1), e1))
    else:
        layers.append(gen_layer(x, y, height*(i+1), e))

output_gcode(layers, output_name, header, footer)

path_b = gen_square(10, 10, gap, -45)
path_c = gen_square(10, 10, 0.5, 180)
path_d = gen_square(10, 10, 0.5, 360)









fig = plt.figure(1, figsize=SIZE, dpi=90)

ax = fig.add_subplot(221)
x2, y2 = path_a.xy
ax.plot(x2, y2)
plot_bounds(ax, path_a)
ax.grid(True)
ax.set_title('A')
plt.axis('equal')

ax = fig.add_subplot(222)
x2, y2 = path_b.xy
ax.plot(x2, y2)
plot_bounds(ax, path_b)
ax.grid(True)
ax.set_title('B')
plt.axis('equal')

ax = fig.add_subplot(223)
x2, y2 = path_c.xy
ax.plot(x2, y2)
plot_bounds(ax, path_c)
ax.grid(True)
ax.set_title('C')
plt.axis('equal')

ax = fig.add_subplot(224)
x2, y2 = path_d.xy
ax.plot(x2, y2)
plot_bounds(ax, path_d)
ax.grid(True)
ax.set_title('D')
plt.axis('equal')

plt.show()
