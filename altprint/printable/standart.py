from altprint.printable.base import BasePrint
from altprint.slicer import STLSlicer
from altprint.layer import Layer, Raster
from altprint.height_method import StandartHeightMethod
from altprint.infill.rectilinear_optimal import RectilinearOptimal
from altprint.flow import calculate
from altprint.gcode import GcodeExporter

class StandartProcess():
    def __init__(self, **kwargs):
        prop_defaults = {
            "model_file": "",
            "slicer": STLSlicer,
            "infill_method": RectilinearOptimal,
            "infill_angle_pattern": [0, 90],
            "center_model": True,
            "position": (100, 100, 0),
            "external_adjust": 0.5,
            "perimeter_num": 2,
            "perimeter_gap": 0.5,
            "raster_gap": 0.5,
            "overlap": 0.0,
            "speed": 2400,
            "flow": calculate(),
            "gcode_exporter": GcodeExporter,
            "start_script": "",
            "end_script": ""
        }

        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))

class StandartPrint(BasePrint):
    """The common print. Nothing special"""

    _height = float
    _layers_dict = dict[_height, Layer]

    def __init__(self, process: StandartProcess):
        self.process = process
        self.layers: _layers_dict = {}
        self.heights: list[float] = []

    def slice(self):
        slicer = self.process.slicer()
        slicer.load_model(self.process.model_file)
        if self.process.center_model:
            slicer.center_model(self.process.position)
        self.sliced_planes = slicer.slice_model(StandartHeightMethod())
        self.heights = self.sliced_planes.get_heights()

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
                                                   self.process.infill_angle_pattern[i%len(self.process.infill_angle_pattern)])
            for path in infill_paths:
                layer.infill.append(Raster(path, self.process.flow, self.process.speed))
            self.layers[height] = layer

    def export_gcode(self, filename):
        gcode_exporter = self.process.gcode_exporter(start_script=self.process.start_script,
                                                     end_script=self.process.end_script)
        gcode_exporter.make_gcode(self)
        gcode_exporter.export_gcode(filename)
