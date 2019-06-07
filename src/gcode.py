def gen_layer(x, y, z, e):
    layer = []
    layer.append('G92 E0.0000\n')
    layer.append('M106 S255\n')
    layer.append('G1 Z{0:.3f} F3000\n'.format(z))
    for i in range(len(x)):
        layer.append('G1 X{0:.3f} Y{1:.3f} E{2:.4f}\n'.format(x[i], y[i], e[i]))
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
    with open('output/' + date + '/' + output_name + '.gcode', 'w') as f:
        f.write(header)
        for layer in layers:
            f.write(layer)
        f.write(footer)
