from altprint.flow import calculate
from shapely.geometry import Polygon, MultiPolygon, LineString
import numpy as np


class Raster:
    def __init__(self, path, z, flow=calculate()):
        self.path = LineString(path)
        self.xy = self.path.xy
        self.z = z
        self.flow = flow

    def extrude(self):
        x, y = self.xy
        extrusion = np.zeros(len(x))
        for i in range(1, len(x)):
            dx = abs(x[i] - x[i - 1])
            dy = abs(y[i] - y[i - 1])
            extrusion[i] = np.sqrt((dx**2) + (dy**2)) * self.flow + extrusion[i-1]
        return extrusion


class Layer:
    def __init__(self, **kwargs):
        prop_defaults = {
            "shape": None,
            "z": 0,
            "perimeters_gap": 0.5,
            "perimeters_num": 2,
            "perimeters": [],
            "infill_shape": [],
            "infill": [],
        }

        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))

        if type(self.shape) != Polygon:
            raise TypeError("shape must be a polygon")

        for i in range(self.perimeters_num):
            eroded = self.shape.buffer(-self.perimeters_gap*i, join_style=2)
            if eroded.is_empty:
                break
            if type(eroded) == Polygon:
                polygons = [eroded]
            elif type(eroded) == MultiPolygon:
                polygons = list(eroded)
            for poly in polygons:
                perimeter = Raster(poly.exterior, self.z)
                self.perimeters.append(perimeter)

        eroded = self.shape.buffer(-self.perimeters_gap *
                                   self.perimeters_num, join_style=2)
        if eroded.is_empty:
            self.infill_shape = []
        else:
            if type(eroded) == Polygon:
                polygons = [eroded]
            elif type(eroded) == MultiPolygon:
                polygons = list(eroded)
            for poly in polygons:
                self.infill_shape.append(poly)
