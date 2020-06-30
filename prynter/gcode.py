import re

def segment(x, y, z, e, v):
    layer = []
    layer.append('; segment\n')
    layer.append('G92 E0.0000\n')
    layer.append('G1 Z{0:.3f} F{1:.3f}\n'.format(z, v))
    layer.append('G1 X{0:.3f} Y{1:.3f}\n'.format(x[0], y[0]))
    for i in range(len(x)-1):
        layer.append('G1 X{0:.3f} Y{1:.3f} E{2:.4f}\n'.format(x[i+1], y[i+1], e[i+1]))
    layer = "".join(layer)
    return layer

def jump(x, y, v=12000):
    layer = []
    layer.append('; jumping\n')
    layer.append('G92 E3.0000\n')
    layer.append('G1 E0 F2400\n')
    layer.append('G1 X{0:.3f} Y{1:.3f} F{2:.3f}\n'.format(x, y, v))
    layer.append('G1 E3 F2400\n')
    layer.append('G92 E0.0000\n')
    layer = "".join(layer)
    return layer

def read_script(fname):
    script = ""
    with open(fname, 'r') as f:
        script = f.readlines()
        script = ''.join(script)
    return script

def output_gcode(layers, output_name, header, footer):
    """
    Generates the final gcode file

    ARGS:
    layers: list containing all layers (str)
    output_name: output file name (str)
    header: gcode file header (str)
    footer: gcode file footer (str)

    """
    with open(output_name + '.gcode', 'w') as f:
        f.write(header)
        for layer in layers:
            f.write(layer)
        f.write(footer)


