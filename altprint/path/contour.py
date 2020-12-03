from collections import deque
from shapely import affinity
from shapely.geometry import LineString
import numpy as np

def contour(border, L):
    """
    Generate a contour line from L milimeters of the shape object.

    ARGS:
    border: LineString of the border (LineString)
    L: distance of the contour from border. Positive numbers means external
    contours, negative numbers means internal contours (float)

    RETURNS:
    LineString containing the contour. (LineString)
    """
    border = border.coords[:-1]
    shape_border = []
    for i in range(len(border)):
        A = border[i-2]
        B = border[i-1]
        C = border[i]

        u = LineString([A,B])
        v = LineString([B,C])

        ux = B[0] - A[0]
        uy = B[1] - A[1]
        vx = C[0] - B[0]
        vy = C[1] - B[1]

        udx = L*uy/u.length
        udy = L*ux/u.length
        vdx = L*vy/v.length
        vdy = L*vx/v.length

        ut = affinity.translate(u,  udx, -udy)
        vt = affinity.translate(v, vdx, -vdy)
        Ax = ut.coords[0][0]
        Ay = ut.coords[0][1]
        Bx = ut.coords[1][0]
        By = ut.coords[1][1]
        Cx = vt.coords[0][0]
        Cy = vt.coords[0][1]
        Dx = vt.coords[1][0]
        Dy = vt.coords[1][1]

        a = np.array([[Ay-By, Bx-Ax], [Cy-Dy, Dx-Cx]])
        b = np.array([Bx*Ay-Ax*By,  Dx*Cy-Cx*Dy])
        x = np.linalg.solve(a, b)

        shape_border.append(x)
    shape_border = deque(shape_border)
    shape_border.rotate(-1)
    shape_border = list(shape_border)
    shape_border.append(shape_border[0])
    return LineString(shape_border)
