from shapely.geometry import LineString
from altprint.printable.base import BasePrint
from altprint.flow import extrude, calculate
import numpy as np
import re

class GcodeExporter:

    def __init__(self, start_script = '', end_script = ''):
        self.gcode_content: list[str] = []
        self.head_x: float = 0.0
        self.head_y: float = 0.0
        self.min_jump: float = 1
        self.start_script_fname = start_script
        self.end_script_fname = end_script

    def segment(self, x, y, z, e, v) -> str:
        segment = []
        segment.append('; segment\n')
        segment.append('G92 E0.0000\n')
        segment.append('G1 F{0:.3f}\n'.format(v[0]))
        if z is not None:
            segment.append('G1 Z{0:.3f}\n'.format(z))
        segment.append('G1 X{0:.3f} Y{1:.3f}\n'.format(x[0], y[0]))

        actual_speed = v[0]
        for i in range(len(x)-1):
            if actual_speed != v[i+1]:
                segment.append('G1 X{0:.3f} Y{1:.3f} E{2:.4f} F{1:.3f} \n'.format(x[i+1], y[i+1], e[i+1], v[i+1]))
                actual_speed = v[i+1]
            else:
                segment.append('G1 X{0:.3f} Y{1:.3f} E{2:.4f} \n'.format(x[i+1], y[i+1], e[i+1]))
        segment.append('G92 E0.0000\n')
        segment = "".join(segment)
        return segment

    def jump(self, x, y, v=12000) -> str:
        jump = []
        jump.append('; jumping\n')
        jump.append('G92 E3.0000\n')
        jump.append('G1 E0 F2400\n')
        jump.append('G1 X{0:.3f} Y{1:.3f} F{2:.3f}\n'.format(x, y, v))
        jump.append('G1 E3 F2400\n')
        jump.append('G92 E0.0000\n')
        jump = "".join(jump)
        return jump


    def read_script(self, fname):
        script = ""
        with open(fname, 'r') as f:
            script = f.readlines()
            script = ''.join(script)
        return script

    def make_gcode(self, printable: BasePrint):

        self.gcode_content = []
        start_script = self.read_script(self.start_script_fname)
        end_script = self.read_script(self.end_script_fname)
        self.gcode_content.append(start_script)

        for z, layer in printable.layers.items():
            for raster in layer.perimeter:
                x, y = raster.path.xy
                x, y = np.array(x), np.array(y)
                if LineString([(self.head_x, self.head_y), (x[0], y[0])]).length > self.min_jump:
                    self.gcode_content.append(self.jump(x[0], y[0]))
                self.head_x, self.head_y = x[-1], y[-1]
                self.gcode_content.append(self.segment(x, y, z, raster.extrusion, raster.speed))

            for raster in layer.infill:
                x, y = raster.path.xy
                x, y = np.array(x), np.array(y)
                if LineString([(self.head_x, self.head_y), (x[0], y[0])]).length > self.min_jump:
                    self.gcode_content.append(self.jump(x[0], y[0]))
                self.head_x, self.head_y = x[-1], y[-1]
                self.gcode_content.append(self.segment(x, y, z, raster.extrusion, raster.speed))

        self.gcode_content.append(end_script)

    def make_layer_gcode(self, layer):
        layer_gcode = []
        for raster in layer.perimeter:
            x, y = raster.path.xy
            x, y = np.array(x), np.array(y)
            if LineString([(self.head_x, self.head_y), (x[0], y[0])]).length > self.min_jump:
                layer_gcode.append(self.jump(x[0], y[0]))
            self.head_x, self.head_y = x[-1], y[-1]
            layer_gcode.append(self.segment(x, y, None, raster.extrusion, raster.speed))

        for raster in layer.infill:
            x, y = raster.path.xy
            x, y = np.array(x), np.array(y)
            if LineString([(self.head_x, self.head_y), (x[0], y[0])]).length > self.min_jump:
                layer_gcode.append(self.jump(x[0], y[0]))
            self.head_x, self.head_y = x[-1], y[-1]
            layer_gcode.append(self.segment(x, y, None, raster.extrusion, raster.speed))

        return layer_gcode

    def export_gcode(self, filename):
        with open(filename, 'w') as f:
            for gcode_block in self.gcode_content:
                f.write(gcode_block)
