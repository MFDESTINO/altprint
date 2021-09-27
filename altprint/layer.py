from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString
import numpy as np
from altprint.flow import calculate


class LayerProcess:
    """Information about layer parameters"""

    def __init__(self, eadj: float = 0.5,
                 pnum: int = 2,
                 pgap: float = 0.5,
                 gap: float = 0.5,
                 overlap: float = 0.0,
                 speed: int = 2400,
                 flow: float = calculate()):
        self.external_adjust = eadj
        self.perimeter_num = pnum
        self.perimeter_gap = pgap
        self.gap = gap
        self.overlap = overlap
        self.speed = speed
        self.flow = flow


class Raster:

    def __init__(self, path: LineString, layer_process: LayerProcess):

        self.path = path

        self.speed = np.ones(len(path.coords)) * layer_process.speed
        self.extrusion = np.zeros(len(path.coords))
        x, y = path.xy
        for i in range(1, len(path.coords)):
            dx = abs(x[i] - x[i - 1])
            dy = abs(y[i] - y[i - 1])
            self.extrusion[i] = np.sqrt((dx**2) + (dy**2)) * layer_process.flow + self.extrusion[i-1]


class Layer:
    """Layer Object that stores layer internal and external shapes, also perimeters and infill path"""

    def __init__(self, shape: MultiPolygon):
        if type(shape) != MultiPolygon:
            raise TypeError("shape must be a MultiPolygon")
        self.shape = shape
        self.perimeter: List
        self.infill: List = []
        self.infill_border: MultiPolygon = MultiPolygon()

    def make_perimeter(self, layer_process: LayerProcess):
        """Generates the perimeter based on the layer process"""

        perimeters = []
        for section in self.shape:
            for i in range(layer_process.perimeter_num):
                eroded_shape = section.buffer(- layer_process.perimeter_gap*(i)
                                              - layer_process.external_adjust/2, join_style=2)

                if eroded_shape.is_empty:
                    break
                if type(eroded_shape) == Polygon:
                    polygons = [eroded_shape]
                elif type(eroded_shape) == MultiPolygon:
                    polygons = list(eroded_shape)

                for poly in polygons:
                    for hole in poly.interiors:
                        perimeters.append(
                            Raster(LineString(hole), layer_process))
                for poly in polygons:
                    perimeters.append(Raster(LineString(poly.exterior), layer_process))
        self.perimeter = perimeters

    def make_infill_border(self, layer_process: LayerProcess):
        """Generates the infill border based on the layer process"""

        infill_border_geoms = []
        for section in self.shape:
            eroded_shape = section.buffer(- layer_process.perimeter_gap
                                          * layer_process.perimeter_num
                                          - layer_process.external_adjust/2
                                          + layer_process.overlap, join_style=2)
            if not eroded_shape.is_empty:
                if type(eroded_shape) == Polygon:
                    infill_border_geoms.append(eroded_shape)
                else:
                    infill_border_geoms.extend(eroded_shape)

        self.infill_border = MultiPolygon(infill_border_geoms)
