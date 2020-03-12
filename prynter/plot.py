from shapely.geometry import LineString, MultiLineString, GeometryCollection


def plot_layer(ax, layer):
    x, y = layer.inner_border.xy
    ax.plot(x, y, color="red")

    for perimeter in layer.perimeters:
        x, y = perimeter.xy
        ax.plot(x, y, linewidth=3, color="green")

    for infill in layer.infill:
        x, y = infill.xy
        ax.plot(x, y, color="blue")
