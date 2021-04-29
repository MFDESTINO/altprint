from altprint.core import Layer
from altprint.path.lineutil import split_by_regions
from altprint.imports.stl import slice_stl
from shapely.geometry import LineString, Polygon, MultiPolygon
from altprint.flow import calculate
from altprint.gcode import segment, jump, segment_to_gcode, read_script
from altprint.gcode import output_gcode as _output_gcode
from altprint.path.rectilinear_fill import rectilinear_fill
from altprint.path.complete_fill import get_remaining_lines


class BasePrint():
    def __init__(self, **kwargs):
        prop_defaults = {
            "model": "",
            "flex_model": "",
            "flow": calculate(),
            "flex_flow": 0,
            "speed": 3000,
            "layer_height": 0.2,
            "table_center": [100, 100, 0],
            "x0": 0,
            "y0": 0,
            "perimeters_gap": 0.5,
            "perimeters_num": 2,
            "complete_fill": True,
            "start_script": "scripts/start.gcode",
            "end_script": "scripts/end.gcode",
        }

        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))
        self.layers = []
        self.START = read_script(self.start_script)
        self.END = read_script(self.end_script)
        self.planes = None
        self.planes_flex = None
        self.translation = None
        self.heights = None

    def slice(self):
        self.planes, self.translation, self.heights = slice_stl(
            self.model, layer_height=self.layer_height, table_center=self.table_center)
        if self.flex_model:
            self.planes_flex, _, _ = slice_stl(
                self.flex_model, heights=self.heights, translation=self.translation)

    def make_layers(self, gap, angle):
        self.layers = []
        for i in range(1, len(self.heights)):
            polygons = self.planes[i]
            if self.flex_model:
                flex_regions = self.planes_flex[i]
            else:
                flex_regions = []

            for poly in polygons:
                layer = Layer(shape=poly, perimeters_num=self.perimeters_num,
                              perimeters_gap=self.perimeters_gap, z=self.heights[i])
                layer.flex_regions = flex_regions
                for shape in layer.infill_shape:
                    infill = rectilinear_fill(shape, gap, angle)
                    layer.infill.extend(infill)
                    if self.complete_fill:
                        layer.complete_fill.extend(get_remaining_lines(shape, infill))

                layer.infill = split_by_regions(layer.infill, layer.flex_regions)
                layer.perimeters = split_by_regions(layer.perimeters, layer.flex_regions)
                if self.complete_fill:
                    layer.complete_fill = split_by_regions(layer.complete_fill, layer.flex_regions)
                self.layers.append(layer)

    def output_gcode(self, output_file):
        layers_gcode = []
        for layer in self.layers:
            for perimeter in layer.perimeters:
                l, self.x0, self.y0 = segment_to_gcode(
                    perimeter, layer.flex_regions, self.flex_flow, self.flow, layer.z, self.speed, self.x0, self.y0)
                layers_gcode.extend(l)
            for infill in layer.infill:
                if not infill.is_empty:
                    l, self.x0, self.y0 = segment_to_gcode(
                        infill, layer.flex_regions, self.flex_flow, self.flow, layer.z, self.speed, self.x0, self.y0)
                    layers_gcode.extend(l)
            if self.complete_fill:
                for infill in layer.complete_fill:
                    if not infill.is_empty:
                        l, self.x0, self.y0 = segment_to_gcode(
                            infill, layer.flex_regions, self.flex_flow, self.flow*0.5, layer.z, self.speed, self.x0, self.y0)
                        layers_gcode.extend(l)

        _output_gcode(layers_gcode, output_file, self.START, self.END)
