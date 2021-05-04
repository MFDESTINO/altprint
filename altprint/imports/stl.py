import numpy as np
import trimesh


def slice_stl(model, layer_height=0.2, heights=None, table_center=[100, 100, 0], translation=None):
    mesh = trimesh.load_mesh(model)
    if translation:
        mesh.apply_translation(translation)
    else:
        mesh_x, mesh_y, mesh_z = mesh.extents
        mesh_center = mesh.bounds[0] + np.array([mesh_x/2, mesh_y/2, 0])
        table_center = np.array(table_center)
        translation = list(table_center - mesh_center)
        mesh.apply_translation(translation)

    if heights:
        sections = mesh.section_multiplane([0, 0, 0], [0, 0, 1], heights)
    else:
        zi = mesh.bounds[0][2]
        zf = mesh.bounds[1][2]
        h = zf - zi
        heights = list(np.linspace(zi, zf, round(h/layer_height)+1))
        heights[-1] = heights[-1]-0.001
        sections = mesh.section_multiplane([0, 0, 0], [0, 0, 1], heights)
    planes = []
    for section in sections:
        if section:
            planes.append(list(section.polygons_full))
        else:
            planes.append([])
    return planes, translation, heights
