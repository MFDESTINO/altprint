import re
import matplotlib.pyplot as plt
from shapely.figures import SIZE, set_limits, plot_line, plot_bounds, color_issimple
from shapely.figures import plot_coords as _plot_coords
import matplotlib.pyplot as plt
from shapely.geometry import LineString
fig = plt.figure(1, figsize=SIZE, dpi=90)
ax = fig.add_subplot(111)

gcode_file = 'elefante.gcode'

G1 = re.compile("G[1]",        re.IGNORECASE)
M = re.compile("M103",         re.IGNORECASE)
X = re.compile("X(\d+\.?\d*)", re.IGNORECASE)
Y = re.compile("Y(\d+\.?\d*)", re.IGNORECASE)
Z = re.compile("Z(\d+\.?\d*)", re.IGNORECASE)
E = re.compile("E(\d+\.?\d*)", re.IGNORECASE)



'''
objeto = [camada1, camada2, camadaN]
camadan = [z, movimento1, movimento2, movimentoN]
movimenton = [line, x, y, e]'''

def parse_gcode(filename):
    with open(filename, 'r') as f:
        gcode = f.readlines()

    z0 = 0
    layer_counter = 0
    move_counter = 0
    gcode_object = [[0, [[],[],[],[]]]]

    for line_counter in range(len(gcode)):
        line = gcode[line_counter]
        if G1.match(line):
            if Z.search(line):
                z = float(Z.findall(line)[0])
                if z != z0:
                    layer_counter += 1
                    move_counter = 0
                    gcode_object.append([z, [[], [], [], []]])
                z0 = z
            if X.search(line) and E.search(line):
                x = float(X.findall(line)[0])
                y = float(Y.findall(line)[0])
                e = float(E.findall(line)[0])
                gcode_object[layer_counter][move_counter+1][0].append(line_counter)
                gcode_object[layer_counter][move_counter+1][1].append(x)
                gcode_object[layer_counter][move_counter+1][2].append(y)
                gcode_object[layer_counter][move_counter+1][3].append(e)
        if M.match(line):
            move_counter += 1
            gcode_object[layer_counter].append([[],[],[],[]])

    return gcode_object, gcode
gcode_parsed, gcode_raw = parse_gcode(gcode_file)


layer = gcode_parsed[2]
x = layer[5][1]
y = layer[5][2]

points = []
for i in range(len(x)):
    points.append((x[i], y[i]))

print(points)
movimento1 = LineString(points)

plot_line(ax, movimento1)
ax.grid(True)
plt.axis('equal')
plt.show()
