from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString
import numpy as np
from altprint.flow import calculate

class Raster:

    def __init__(self, path: LineString, flow, speed):

        self.path = path

        self.speed = np.ones(len(path.coords)) * speed
        self.extrusion = np.zeros(len(path.coords))
        x, y = path.xy
        for i in range(1, len(path.coords)):
            dx = abs(x[i] - x[i - 1])
            dy = abs(y[i] - y[i - 1])
            self.extrusion[i] = np.sqrt((dx**2) + (dy**2)) * flow * calculate() + self.extrusion[i-1]


class Layer:
    """Layer Object that stores layer internal and external shapes, also perimeters and infill path"""

    def __init__(self, shape: MultiPolygon, perimeter_num, perimeter_gap, external_adjust, overlap):
        self.shape = shape
        self.perimeter_num = perimeter_num
        self.perimeter_gap = perimeter_gap
        self.external_adjust = external_adjust
        self.overlap = overlap
        self.perimeter_paths: List = []
        self.perimeter: List = []
        self.infill: List = []
        self.infill_border: MultiPolygon = MultiPolygon()

    def make_perimeter(self):
        """Generates the perimeter based on the layer process"""

        perimeter_paths = []
        for section in self.shape.geoms:
            for i in range(self.perimeter_num):
                eroded_shape = section.buffer(- self.perimeter_gap*(i)
                                              - self.external_adjust/2, join_style=2)

                if eroded_shape.is_empty:
                    break
                if type(eroded_shape) == Polygon:
                    polygons = [eroded_shape]
                elif type(eroded_shape) == MultiPolygon:
                    polygons = list(eroded_shape.geoms)

                for poly in polygons:
                    for hole in poly.interiors:
                        perimeter_paths.append(LineString(hole))
                for poly in polygons:
                    perimeter_paths.append(LineString(poly.exterior))
        self.perimeter_paths = MultiLineString(perimeter_paths)

    def make_infill_border(self):
        """Generates the infill border based on the layer process"""

        infill_border_geoms = []
        for section in self.shape.geoms:
            eroded_shape = section.buffer(- self.perimeter_gap
                                          * self.perimeter_num
                                          - self.external_adjust/2
                                          + self.overlap, join_style=2)
            if not eroded_shape.is_empty:
                if type(eroded_shape) == Polygon:
                    infill_border_geoms.append(eroded_shape)
                else:
                    infill_border_geoms.extend(eroded_shape.geoms)

        self.infill_border = MultiPolygon(infill_border_geoms)
