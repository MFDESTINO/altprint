from shapely.geometry import LineString, MultiLineString

def border_to_lines(border_coords):
    border_lines = []
    for i in range(1, len(border_coords)):
        line = LineString([border_coords[i-1], border_coords[i]])
        border_lines.append(line)
    return border_lines

def poly_to_lines(shape):
    border_lines = []
    border_lines.extend(border_to_lines(shape.exterior.coords))
    for hole in shape.interiors:
        border_lines.extend(border_to_lines(hole.coords))
    return border_lines

def get_remaining_lines(shape, infill):
    border_lines = poly_to_lines(shape)
    infill = MultiLineString(infill)
    remaining_lines = []
    for line in border_lines:
        if not line.intersects(infill):
            remaining_lines.append(line)
    return remaining_lines

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from shapely.geometry import Polygon
    from altprint.path.rectilinear_fill import rectilinear_fill

    ax = plt.subplot()
    ax.axis('equal')

    border = [(0, 0), (10, 0), (10, 10), (20, 10), (20, 5), (30, 5), (30, 40), (10,25), (0, 30)]
    holes = [[(5, 15), (15, 15), (15, 20), (5, 20)], [(20, 25), (25, 25), (25, 30)]]
    shape = Polygon(border, holes)
    gap, angle = 0.6, 0
    paths = rectilinear_fill(shape, gap, angle)

    remaining_lines = get_remaining_lines(shape, paths)

    for line in remaining_lines:
        x, y = line.xy
        ax.plot(x, y, color="red")

    for path in paths:
        x, y = path.xy
        ax.plot(x, y, color="gray")
    plt.show()
