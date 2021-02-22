import numpy as np

def calculate(w = 0.48, h = 0.2, df = 1.75, adjust = 1.2):
    """
    Calculates the flow multiplier factor, using the rounded rectangle model.

    ARGS:
    w: raster width (default 0.48mm) (float)
    h: raster height (default 0.2mm) (float)
    df: filament diameter (default 1.75mm) (float)
    adjust: adjust factor (default 100%) (float)

    RETURNS:
    Flow multiplier factor
    """
    a = 4 * w * h + (np.pi - 4) * h**2
    b = np.pi * df**2
    flow = adjust * a / b
    return flow


def extrude(x, y, flow):
    """
    Generates the extrusion coordinate array.

    ARGS:
    x: x array (array)
    y: y array (array)
    flow: flow multiplier (float)
    RETURNS:
    Extrusion coordinate array (array)
    """
    extrusion = np.zeros(len(x))
    for i in range(1, len(x)):
        dx = abs(x[i] - x[i - 1])
        dy = abs(y[i] - y[i - 1])
        extrusion[i] = np.sqrt((dx**2) + (dy**2)) * flow + extrusion[i-1]
    return extrusion
