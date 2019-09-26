def gen_layer(x, y, z, e):
    layer = []
    layer.append('G1 Z{0:.3f} F3000\n'.format(z))
    layer.append('G1 X{0:.3f} Y{1:.3f}\n'.format(x[0], y[0]))
    layer.append('M101\n')
    layer.append('G1 E0.0000\n')
    layer.append('G92 E0.0000\n')
    for i in range(len(x)-1):
        layer.append('G1 X{0:.3f} Y{1:.3f} E{2:.4f}\n'.format(x[i+1], y[i+1], e[i+1]))
    layer.append('M102\n')
    layer.append('G92 E0.0000\n')
    layer.append('G1 E-0.5000\n')
    layer.append('M103\n')
    layer = "".join(layer)
    return layer

def output_gcode(layers, output_name, date, header, footer):
    """
    Gera o arquivo gcode final.

    Args:
    x: vetor com as componentes x dos pontos
    y: vetor com as componentes y dos pontos
    e: vetor com as coordenadas da extrusão do filamento.
    output_name: nome do arquivo de saída
    header: cabeçalho do arquivo de saída
    footer: rodapé do arquivo de saída

    """
    with open(output_name + '.gcode', 'w') as f:
        f.write(header)
        for layer in layers:
            f.write(layer)
        f.write(footer)
