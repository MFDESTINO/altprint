from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import time

from rectilinear_infill import rectilinear_fill
from altprint.infill.rectilinear_optimal import rectilinear_optimal as rectilinear_fill_old

border = [(0, 0), (10, 0), (10, 10), (20, 10), (20, 5), (30, 5), (30, 40), (10,25), (0, 30)]
holes = [[(5, 15), (15, 15), (15, 20), (5, 20)], [(20, 25), (25, 25), (25, 30)]]
poly = Polygon(border, holes)
gap = 0.1
thres = 0
angle = 20

paths = rectilinear_fill(poly, gap, angle, thres)

paths_old = rectilinear_fill_old(poly, gap, angle)

tdelta = 0
N = 3
for i in range(N):
    start_time = time.time()
    rectilinear_fill(poly, gap, angle, thres)
    tdelta = tdelta + time.time() - start_time
new_time = tdelta/N

tdelta = 0
for i in range(N):
    start_time = time.time()
    rectilinear_fill_old(poly, gap, angle)
    tdelta = tdelta + time.time() - start_time
old_time = tdelta/N


print("--- New time:  ---")
print("--- %s seconds ---" % (new_time))

print("--- Old time:  ---")
print("--- %s seconds ---" % (old_time))

fig, axs = plt.subplots(1, 2, sharey=True)


fig.suptitle('Polígono de {:.2f}mm com gap de {:.2f}mm'.format(poly.bounds[3]-poly.bounds[1], gap))

x, y = poly.exterior.xy
axs[0].plot(x, y, color="black", linewidth=3)
axs[1].plot(x, y, color="black", linewidth=3)
for hole in poly.interiors:
    x, y = hole.xy
    axs[0].plot(x, y, color="black", linewidth=3)
    axs[1].plot(x, y, color="black", linewidth=3)
axs[0].set_title("Algoritmo novo\nTempo médio: {:.1f} ms".format(new_time*1000))
axs[1].set_title("Algoritmo antigo (optimal)\nTempo médio: {:.1f} ms".format(old_time*1000))
for path in paths.geoms:
    x, y = path.xy
    axs[0].plot(x, y, linewidth=2)

for path in paths_old:
    x, y = path.xy
    axs[1].plot(x, y, linewidth=2)
axs[0].axis("equal")
axs[1].axis("equal")
plt.show()