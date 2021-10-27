from altprint.printable.base import BasePrint
from altprint.slicer import STLSlicer
from altprint.layer import Layer, Raster
from altprint.height_method import StandartHeightMethod
from altprint.infill.rectilinear_optimal import RectilinearOptimal
from altprint.flow import calculate
from altprint.gcode import GcodeExporter
from altprint.lineutil import split_by_regions, retract

class FlexProcess():
    def __init__(self, **kwargs):
        prop_defaults = {
            "model_file": "",
            "flex_model_file": "",
            "slicer": STLSlicer,
            "infill_method": RectilinearOptimal,
            "infill_angle": 0,
            "center_model": True,
            "position": (100, 100, 0),
            "external_adjust": 0.5,
            "perimeter_num": 2,
            "perimeter_gap": 0.5,
            "raster_gap": 0.5,
            "overlap": 0.0,
            "flow": calculate(),
            "speed": 2400,
            "flex_flow": 0,
            "flex_speed": 2000,
            "retract_flow": 2 * calculate(),
            "retract_speed": 1200,
            "retract_ratio": 0.9,
            "gcode_exporter": GcodeExporter,
            "start_script": "",
            "end_script": ""
        }

        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))

class FlexPrint(BasePrint):
    """The common print. Nothing special"""

    _height = float
    _layers_dict = dict[_height, Layer]

    def __init__(self, process: FlexProcess):
        self.process = process
        self.layers: _layers_dict = {}
        self.heights: list[float] = []

    def slice(self):
        slicer = self.process.slicer()
        slicer.load_model(self.process.model_file)
        if self.process.center_model:
            translation = slicer.center_model(self.process.position)
        self.sliced_planes = slicer.slice_model(StandartHeightMethod())
        self.heights = self.sliced_planes.get_heights()

        slicer.load_model(self.process.flex_model_file)
        if self.process.center_model:
            slicer.translate_model(translation)
        self.flex_planes = slicer.slice_model(StandartHeightMethod(), self.heights)

    def make_layers(self):
        infill_method = self.process.infill_method()
        for i, height in enumerate(self.heights):
            layer = Layer(self.sliced_planes.planes[height],
                          self.process.perimeter_num,
                          self.process.perimeter_gap,
                          self.process.external_adjust,
                          self.process.overlap)
            layer.make_perimeter(self.process.flow, self.process.speed)
            layer.make_infill_border()
            infill_paths = infill_method.generate_infill(layer,
                                                   self.process.raster_gap,
                                                   self.process.infill_angle)
            flex_regions = self.flex_planes.planes[height]
            infill_paths = split_by_regions(infill_paths, flex_regions)

            for path in infill_paths:
                flex_path = False
                for region in flex_regions:
                    if path.within(region):
                        flex_path, retract_path = retract(path, self.process.retract_ratio)
                        layer.infill.append(Raster(flex_path, self.process.flex_flow, self.process.flex_speed))
                        layer.infill.append(Raster(retract_path, self.process.retract_flow, self.process.retract_speed))
                        flex_path = True
                        break
                if not flex_path:
                    layer.infill.append(Raster(path, self.process.flow, self.process.speed))
            self.layers[height] = layer

    def export_gcode(self, filename):
        gcode_exporter = self.process.gcode_exporter(start_script=self.process.start_script,
                                                     end_script=self.process.end_script)
        gcode_exporter.make_gcode(self)
        gcode_exporter.export_gcode(filename)
