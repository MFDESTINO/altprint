import ezdxf

def parse_line(e):
    E = 9
    line = [(round(e.dxf.start[0], E), round(e.dxf.start[1], E)),
            (round(e.dxf.end[0], E), round(e.dxf.end[1], E))]
    return(line)


def read_dxf(file, layer):
    bounds = []
    doc = ezdxf.readfile(file)
    msp = doc.modelspace()
    for entity in msp:
        if entity.dxftype() == "LINE":
            if entity.dxf.layer == layer:
                bounds.append(parse_line(entity)[0])
    bounds.append(bounds[0])
    return bounds
