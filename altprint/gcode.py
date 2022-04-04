from shapely.geometry import LineString
from altprint.printable.base import BasePrint
from altprint.flow import extrude, calculate
import numpy as np
import re

class GcodeExporter:

    def __init__(self, start_script, end_script):
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
        segment.append('G1 Z{0:.3f} F{1:.3f}\n'.format(z, v[0]))
        segment.append('G1 X{0:.3f} Y{1:.3f}\n'.format(x[0], y[0]))

        actual_speed = v[0]
        for i in range(len(x)-1):
            if actual_speed != v[i+1]:
                segment.append('G1 X{0:.3f} Y{1:.3f} E{2:.4f} F{1:.3f} \n'.format(x[i+1], y[i+1], e[i+1], v[i+1]))
                actual_speed = v[i+1]
            else:
                segment.append('G1 X{0:.3f} Y{1:.3f} E{2:.4f} \n'.format(x[i+1], y[i+1], e[i+1]))
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

        dx, dy, dz = printable.process.offset #offset of the print

        for z, layer in printable.layers.items():
            for raster in layer.perimeter:
                x, y = raster.path.xy
                x, y = np.array(x) + dx, np.array(y) + dy
                if LineString([(self.head_x, self.head_y), (x[0], y[0])]).length > self.min_jump:
                    self.gcode_content.append(self.jump(x[0], y[0]))
                self.head_x, self.head_y = x[-1], y[-1]
                self.gcode_content.append(self.segment(x, y, z+dz, raster.extrusion, raster.speed))

            for raster in layer.infill:
                x, y = raster.path.xy
                x, y = np.array(x) + dx, np.array(y) + dy
                if LineString([(self.head_x, self.head_y), (x[0], y[0])]).length > self.min_jump:
                    self.gcode_content.append(self.jump(x[0], y[0]))
                self.head_x, self.head_y = x[-1], y[-1]
                self.gcode_content.append(self.segment(x, y, z+dz, raster.extrusion, raster.speed))

        self.gcode_content.append(end_script)

    def inject_gcode(self, printable: BasePrint, destination_file):

        self.gcode_content = []
        self.gcode_content_by_z = {}

        dx, dy, dz = printable.process.offset #offset of the print

        for z, layer in printable.layers.items():
            print(z)
            self.gcode_content_by_z[z] = []
            for raster in layer.perimeter:
                x, y = raster.path.xy
                x, y = np.array(x) + dx, np.array(y) + dy
                if LineString([(self.head_x, self.head_y), (x[0], y[0])]).length > self.min_jump:
                    self.gcode_content_by_z[z].append(self.jump(x[0], y[0]))
                self.head_x, self.head_y = x[-1], y[-1]
                self.gcode_content_by_z[z].append(self.segment(x, y, z+dz, raster.extrusion, raster.speed))

            for raster in layer.infill:
                x, y = raster.path.xy
                x, y = np.array(x) + dx, np.array(y) + dy
                if LineString([(self.head_x, self.head_y), (x[0], y[0])]).length > self.min_jump:
                    self.gcode_content_by_z[z].append(self.jump(x[0], y[0]))
                self.head_x, self.head_y = x[-1], y[-1]
                self.gcode_content_by_z[z].append(self.segment(x, y, z+dz, raster.extrusion, raster.speed))

        with open(destination_file, "r") as f:
            lines = f.readlines()

        zexp = re.compile('Z[\d]*[\.[\d]+]?')

        last_z = 1000
        print(self.gcode_content_by_z.keys())
        for line in lines:
            z = zexp.findall(line)
            if z:
                z_index = float(z[0][1:])
                if z_index - last_z > 0:
                    if z_index in self.gcode_content_by_z.keys():
                        self.gcode_content.append(line)
                        self.gcode_content.append('; INSERTED BY ALTPRINT\n')
                        self.gcode_content.append('M101\n')
                        self.gcode_content.extend(self.gcode_content_by_z[z_index])
                        self.gcode_content.append('M102\nG92 E0.0000\nG1 E-1.0000 F2400\nM103\n')
                        self.gcode_content.append('; END OF INSERTION\n')
                    else:
                        print('index mismatch: {}'.format(z_index))
                last_z = z_index
            self.gcode_content.append(line)

    def export_gcode(self, filename):
        with open(filename, 'w') as f:
            for gcode_block in self.gcode_content:
                f.write(gcode_block)
