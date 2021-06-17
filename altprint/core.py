from altprint.flow import calculate
from shapely.geometry import Polygon, MultiPolygon, LineString
import numpy as np


class Layer:
    def __init__(self, **kwargs):
        prop_defaults = {
            "shape": None,
            "z": 0,
            "external_adjust": 0.5,
            "perimeters_gap": 0.5,
            "perimeters_num": 2,
            "overlap": 0,
            "perimeters": [],
            "infill_shape": [],
            "infill": [],
            "complete_fill": [],
            "flex_regions": [],
            "print_params": {},
        }

        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))

        if type(self.shape) != Polygon:
            raise TypeError("shape must be a polygon")

        for i in range(self.perimeters_num):
            eroded = self.shape.buffer(-self.perimeters_gap*(i)
                                        - self.external_adjust/2, join_style=2)
            if eroded.is_empty:
                break
            if type(eroded) == Polygon:
                polygons = [eroded]
            elif type(eroded) == MultiPolygon:
                polygons = list(eroded)
            for poly in polygons:
                for hole in poly.interiors:
                    self.perimeters.append(LineString(hole))
            for poly in polygons:
                self.perimeters.append(LineString(poly.exterior))

        eroded = self.shape.buffer(-self.perimeters_gap *
                                   self.perimeters_num - self.external_adjust/2 + self.overlap, join_style=2)
        if eroded.is_empty:
            self.infill_shape = []
        else:
            if type(eroded) == Polygon:
                polygons = [eroded]
            elif type(eroded) == MultiPolygon:
                polygons = list(eroded)
            for poly in polygons:
                self.infill_shape.append(poly)
