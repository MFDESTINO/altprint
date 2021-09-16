from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString


class LayerProcess:
    """Information about layer parameters"""

    def __init__(self, eadj: float = 0.5, pnum: int = 2, pgap: float = 0.5, overlap: float = 0.0):
        self.external_adjust = eadj
        self.perimeter_num = pnum
        self.perimeter_gap = pgap
        self.overlap = overlap


class Layer:
    """Layer Object that stores layer internal and external shapes, also perimeters and infill path"""

    def __init__(self, shape: MultiPolygon):
        if type(shape) != MultiPolygon:
            raise TypeError("shape must be a MultiPolygon")
        self.shape = shape
        self.perimeter: MultiLineString = MultiLineString()
        self.infill: MultiLineString = MultiLineString()
        self.infill_border: MultiPolygon = MultiPolygon()

    def make_perimeter(self, layer_process: LayerProcess):
        """Generates the perimeter based on the layer process"""

        perimeter_geoms = []
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
                        perimeter_geoms.append(LineString(hole))
                for poly in polygons:
                    perimeter_geoms.append(LineString(poly.exterior))
        self.perimeter = MultiLineString(perimeter_geoms)

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
