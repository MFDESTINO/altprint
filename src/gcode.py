def gen_layer(x, y, z, e):
    """
    Transforma em gcode as coordenadas correspondentes a uma camada

    Args:
    x: vetor com as componentes x dos pontos
    y: vetor com as componentes y dos pontos
    z: altura z da camada
    e: vetor com as coordenadas de extrusao

    Returns:
    layer: string contendo o gcode correspondente a uma camada
    """
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

def output_gcode(layers, output_name, header, footer):
    """
    Gera o arquivo gcode final.

    Args:
    layers: lista contendo todas as camadas a serem impressas
    output_name: nome do arquivo de saída
    header: cabeçalho gcode do arquivo de saída
    footer: rodapé gcode do arquivo de saída

    """
    with open(output_name + '.gcode', 'w') as f:
        f.write(header)
        for layer in layers:
            f.write(layer)
        f.write(footer)
