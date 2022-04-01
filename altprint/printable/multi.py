from altprint.printable.base import BasePrint
from altprint.layer import Layer
from altprint.gcode import GcodeExporter

class MultiProcess():
    def __init__(self, **kwargs):
        prop_defaults = {
            "parts": [],
            "gcode_exporter": GcodeExporter,
            "start_script": "",
            "end_script": "",
            "offset": (0,0,0),
            "verbose": True,
        }

        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))

class MultiPrint(BasePrint):

    _height = float
    _layers_dict = dict[_height, Layer]

    def __init__(self, process):
        self.process = process
        self.layers: _layers_dict = {}

    def slice(self):
        pass

    def make_layers(self):
        if self.process.verbose == True:
            print("Making the layers for the multipart ...")
        heights = []
        for part in self.process.parts:
            heights.extend(list(part.layers.keys()))

        heights = list(set(heights))
        heights.sort()

        for h in heights:
            layer = Layer(None, None, None, None, None)
            for part in self.process.parts:
                if h in part.layers.keys():
                    layer.infill.extend(part.layers[h].infill)
                    layer.perimeter.extend(part.layers[h].perimeter)
            self.layers[h] = layer

    def export_gcode(self, filename):
        if self.process.verbose == True:
            print("exporting gcode to {}".format(filename))
        gcode_exporter = self.process.gcode_exporter(start_script=self.process.start_script,
                                                     end_script=self.process.end_script)
        gcode_exporter.make_gcode(self)
        gcode_exporter.export_gcode(filename)
