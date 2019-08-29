from shapely.figures import SIZE, set_limits, plot_line, plot_bounds, color_issimple
from shapely.figures import plot_coords as _plot_coords
import matplotlib.pyplot as plt

fig = plt.figure(1, figsize=SIZE, dpi=90)
ax = fig.add_subplot(111)

def plot_coords(ax, ob, color='gray'):
    for line in ob:
        _plot_coords(ax, line, color=color, zorder=3)

def plot_lines(ax, ob, color='gray'):
    for line in ob:
        plot_line(ax, line, color=color, zorder=2)

def plot_layer(layer):
    for p in layer.perimeters:
        x, y = p.xy
        ax.plot(x,y, linewidth=2)
    x, y = layer.inner_shape.xy
    ax.plot(x,y, linewidth=2)
    ax.grid(True)
    plt.axis('equal')
    plt.show()
