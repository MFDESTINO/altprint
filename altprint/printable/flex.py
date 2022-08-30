from altprint.printable.base import BasePrint
from altprint.slicer import STLSlicer
from altprint.layer import Layer, Raster
from altprint.height_method import StandartHeightMethod
from altprint.infill.rectilinear_optimal import RectilinearOptimal
from altprint.flow import calculate
from altprint.gcode import GcodeExporter
from altprint.lineutil import split_by_regions, retract
from altprint.settingsparser import SettingsParser

class FlexProcess():
    def __init__(self, **kwargs):
        prop_defaults = {
            "model_file": "",
            "flex_model_file": "",
            "slicer": STLSlicer(StandartHeightMethod()),
            "infill_method": RectilinearOptimal,
            "infill_angle": 0,
            "offset": (0, 0, 0),
            "external_adjust": 0.5,
            "perimeter_num": 1,
            "perimeter_gap": 0.5,
            "raster_gap": 0.5,
            "overlap": 0.0,
            "skirt_distance": 10,
            "skirt_num": 3,
            "skirt_gap": 0.5,
            "first_layer_flow": 2,
            "flow": 1.2,
            "speed": 2400,
            "flex_flow": 0,
            "flex_speed": 2000,
            "retract_flow": 2,
            "retract_speed": 1200,
            "retract_ratio": 0.9,
            "gcode_exporter": GcodeExporter,
            "start_script": "",
            "end_script": "",
            "verbose": True,
        }

        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))
        
        if 'settings_file' in kwargs.keys():
            settings = SettingsParser().load_from_file(kwargs['settings_file'])
            for (setting, value) in settings.items():
                setattr(self, setting, value)


class FlexPrint(BasePrint):
    """The common print. Nothing special"""

    _height = float
    _layers_dict = dict[_height, Layer]

    def __init__(self, process: FlexProcess):
        self.process = process
        self.layers: _layers_dict = {}
        self.heights: list[float] = []

    def slice(self):
        if self.process.verbose == True:
            print("slicing {} ...".format(self.process.model_file))
        slicer = self.process.slicer
        slicer.load_model(self.process.model_file)
        slicer.translate_model(self.process.offset)
        self.sliced_planes = slicer.slice_model()
        self.heights = self.sliced_planes.get_heights()

        slicer.load_model(self.process.flex_model_file)
        slicer.translate_model(self.process.offset)
        self.flex_planes = slicer.slice_model(self.heights)

    def make_layers(self):
        if self.process.verbose == True:
            print("generating layers ...")
        infill_method = self.process.infill_method()
        
        skirt = Layer(self.sliced_planes.planes[self.heights[0]],
                      self.process.skirt_num,
                      self.process.skirt_gap,
                      - self.process.skirt_distance - self.process.skirt_gap * self.process.skirt_num,
                      self.process.overlap)
        skirt.make_perimeter()

        for i, height in enumerate(self.heights):
            layer = Layer(self.sliced_planes.planes[height],
                          self.process.perimeter_num,
                          self.process.perimeter_gap,
                          self.process.external_adjust,
                          self.process.overlap)
            if layer.shape == []:
                self.layers[height] = layer
                continue
            layer.make_perimeter()
            layer.make_infill_border()
            infill_paths = infill_method.generate_infill(layer,
                                                   self.process.raster_gap,
                                                   self.process.infill_angle)
            flex_regions = self.flex_planes.planes[height]

            if not type(flex_regions) == list:
                flex_regions = list(flex_regions.geoms)

            layer.perimeter_paths = split_by_regions(layer.perimeter_paths, flex_regions)
            infill_paths = split_by_regions(infill_paths, flex_regions)
            if i==0: #skirt
                for path in skirt.perimeter_paths.geoms:
                    layer.perimeter.append(Raster(path, self.process.first_layer_flow, self.process.speed))
            for path in layer.perimeter_paths.geoms:
                flex_path = False
                for region in flex_regions:
                    if path.within(region.buffer(0.01, join_style=2)):
                        flex_path, retract_path = retract(path, self.process.retract_ratio)
                        layer.perimeter.append(Raster(flex_path, self.process.flex_flow, self.process.flex_speed))
                        layer.perimeter.append(Raster(retract_path, self.process.retract_flow, self.process.retract_speed))
                        flex_path = True
                        break
                if not flex_path:
                    if i==0: 
                        layer.perimeter.append(Raster(path, self.process.first_layer_flow, self.process.speed))
                    else:
                        layer.perimeter.append(Raster(path, self.process.flow, self.process.speed))

            for path in infill_paths.geoms:
                flex_path = False
                for region in flex_regions:
                    if path.within(region.buffer(0.01, join_style=2)):
                        flex_path, retract_path = retract(path, self.process.retract_ratio)
                        layer.infill.append(Raster(flex_path, self.process.flex_flow, self.process.flex_speed))
                        layer.infill.append(Raster(retract_path, self.process.retract_flow, self.process.retract_speed))
                        flex_path = True
                        break
                if not flex_path:
                    if i==0:
                        layer.infill.append(Raster(path, self.process.first_layer_flow, self.process.speed))
                    else:
                        layer.infill.append(Raster(path, self.process.flow, self.process.speed))
            self.layers[height] = layer

    def export_gcode(self, filename):
        if self.process.verbose == True:
            print("exporting gcode to {}".format(filename))

        gcode_exporter = self.process.gcode_exporter(start_script=self.process.start_script,
                                                     end_script=self.process.end_script)
        gcode_exporter.make_gcode(self)
        gcode_exporter.export_gcode(filename)
