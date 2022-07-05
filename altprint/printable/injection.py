from altprint.printable.base import BasePrint
from altprint.slicer import STLSlicer
from altprint.height_method import CopyHeightsFromFileMethod
from altprint.gcode import GcodeExporter


class InjectionProcess():
    def __init__(self, **kwargs):
        prop_defaults = {
            "parts": [],
            "parts_offset": [0,0,0],
            "source_gcode": '',
            "verbose": True,
        }

        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))

class InjectionPrint(BasePrint):
    """Base Printable Object"""

    def __init__(self, process: InjectionProcess):
        self.process = process
        self.layers: _layers_dict = {}
        self.layers_gcode = {}
        for part in self.process.parts:
            part.process.slicer = STLSlicer(CopyHeightsFromFileMethod(self.process.source_gcode))
            part.process.offset = self.process.parts_offset

    def slice(self):
        for part in self.process.parts:
            part.slice()

    def make_layers(self):
        for part in self.process.parts:
            part.make_layers()

    def make_layers_gcode(self):
        gcode_exporter = GcodeExporter()
        heights = CopyHeightsFromFileMethod(self.process.source_gcode).get_heights()
        for height in heights:
            layer_gcode = []
            for part in self.process.parts:
                layer_gcode.extend(gcode_exporter.make_layer_gcode(part.layers[height]))
            self.layers_gcode[height] = layer_gcode
        
    def export_gcode(self, filename):
        self.make_layers_gcode()
        output_lines = []
        with open(self.process.source_gcode, "r") as f:
            lines = f.readlines()
        for line in lines:
            output_lines.append(line)
            if line.startswith("; ALTPRINT"):
                height = float(line.split(' ')[-1])
                output_lines.extend(self.layers_gcode[height])
            
        with open(filename, "w") as f:
            for line in output_lines:
                f.write(line)