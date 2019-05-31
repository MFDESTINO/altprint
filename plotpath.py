from shapely.figures import SIZE, set_limits, plot_line, plot_bounds, color_issimple
from shapely.figures import plot_coords as _plot_coords

def plot_coords(ax, ob, color='gray'):
    for line in ob:
        _plot_coords(ax, line, color=color, zorder=3)

def plot_lines(ax, ob, color='gray'):
    for line in ob:
        plot_line(ax, line, color=color, zorder=2)
