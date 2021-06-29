from altprint.core import Layer
from altprint.path.lineutil import split_by_regions
from altprint.imports.stl import slice_stl
from shapely.geometry import LineString, Polygon, MultiPolygon
from shapely.affinity import rotate, translate
from altprint.flow import calculate
from altprint.gcode import segment, jump, read_script, segment_to_gcode
from altprint.gcode import output_gcode as _output_gcode
from altprint.path.rectilinear_fill import rectilinear_fill
from altprint.path.complete_fill import get_remaining_lines
import json

class BasePrint():
    def __init__(self, **kwargs):
        prop_defaults = {
            "model": "",
            "flex_model": "",
            "print_params": {"flow": calculate(adjust=1),
                             "speed": 2100,
                             "flex_ratio": 0.9,
                             "flex_flow1": calculate(adjust=0),
                             "flex_flow2": calculate(adjust=2),
                             "flex_speed1": 1900,
                             "flex_speed2": 1200 },
            "layer_height": 0.2,
            "table_center": [100, 100, 0],
            "x0": 0,
            "y0": 0,
            "perimeters_gap": 0.5,
            "perimeters_num": 2,
            "overlap": 0,
            "complete_fill": True,
            "start_script": "scripts/start.gcode",
            "end_script": "scripts/end.gcode",
        }

        self.params = []
        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))
            self.params.append(prop)
        self.layers = []
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

    def _rotate_layer(self, layer, rotation):
        for i in range(len(layer.perimeters)):
            layer.perimeters[i] = rotate(layer.perimeters[i], rotation, (100, 100))
        for i in range(len(layer.infill)):
            layer.infill[i] = rotate(layer.infill[i], rotation, (100, 100))
        for i in range(len(layer.complete_fill)):
            layer.complete_fill[i] = rotate(layer.complete_fill[i], rotation, (100, 100))
        for i in range(len(layer.flex_regions)):
            layer.flex_regions[i] = rotate(layer.flex_regions[i], rotation, (100, 100)).buffer(0.1, join_style=2)
        return layer

    def make_layers(self, gap, angle, rotation=0, fill=rectilinear_fill):
        self.layers = []
        for i in range(1, len(self.heights)):
            polygons = self.planes[i]
            if i==1:
                bounds = MultiPolygon(polygons).bounds
                border_coords = [(bounds[0], bounds[1]),
                                 (bounds[2], bounds[1]),
                                 (bounds[2], bounds[3]),
                                 (bounds[0], bounds[3])]
                border = Polygon(border_coords).buffer(2, join_style=2)
                brim = Layer(shape=border, perimeters_num=3, print_params=self.print_params,
                              perimeters_gap=self.perimeters_gap, overlap=self.overlap, z=self.heights[i])
                brim_rotated = self._rotate_layer(brim, rotation)
                self.layers.append(brim_rotated)
            if self.flex_model:
                flex_regions = self.planes_flex[i]
            else:
                flex_regions = []

            for poly in polygons:
                layer = Layer(shape=poly, perimeters_num=self.perimeters_num, print_params=self.print_params,
                              perimeters_gap=self.perimeters_gap, overlap=self.overlap, z=self.heights[i])
                layer.flex_regions = flex_regions
                for shape in layer.infill_shape:
                    infill = fill(shape, gap, angle)
                    layer.infill.extend(infill)
                    if self.complete_fill:
                        layer.complete_fill.extend(get_remaining_lines(shape, infill))

                layer.infill = split_by_regions(layer.infill, layer.flex_regions)
                layer.perimeters = split_by_regions(layer.perimeters, layer.flex_regions)
                if self.complete_fill:
                    layer.complete_fill = split_by_regions(layer.complete_fill, layer.flex_regions)
                layer_rotated = self._rotate_layer(layer, rotation)
                self.layers.append(layer_rotated)

    def output_gcode(self, output_file):
        layers_gcode = []
        header_comment = {}
        for param in self.params:
            header_comment[param] = getattr(self, param)
        header_comment = json.dumps(header_comment, indent=2)
        header_comment = '\n;'.join(header_comment.split('\n'))[2:-2]
        for layer in self.layers:
            for perimeter in layer.perimeters:
                l, self.x0, self.y0 = segment_to_gcode(
                    perimeter, layer.flex_regions, layer.print_params, layer.z, self.x0, self.y0)
                layers_gcode.extend(l)
            for infill in layer.infill:
                if not infill.is_empty:
                    l, self.x0, self.y0 = segment_to_gcode(
                        infill, layer.flex_regions, layer.print_params, layer.z, self.x0, self.y0)
                    layers_gcode.extend(l)
            if self.complete_fill:
                for infill in layer.complete_fill:
                    if not infill.is_empty:
                        l, self.x0, self.y0 = segment_to_gcode(
                            infill, layer.flex_regions, layer.print_params, layer.z, self.x0, self.y0)
                        layers_gcode.extend(l)
        START = read_script(self.start_script)
        END = read_script(self.end_script)
        _output_gcode(layers_gcode, output_file, START, END, header_comment)
