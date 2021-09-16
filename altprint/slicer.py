from abc import ABC, abstractmethod
import numpy as np
import trimesh
from shapely.geometry import MultiPolygon
from altprint.height_method import HeightMethod

class SlicedPlanes:
    """Represents the section planes obtained from the slicing of an object"""

    _height = float
    _planes_dict = dict[_height, MultiPolygon]
    _coord = tuple[float, float, float]
    _bounds_coords = tuple[_coord, _coord]

    def __init__(self, planes: _planes_dict, bounds : _bounds_coords):

        self.planes = planes
        self.bounds = bounds

    def get_heights(self):
        return list(self.planes.keys())


class Slicer(ABC):
    """Slicer base object"""

    @abstractmethod
    def slice_model(self, model: str, height_method: HeightMethod) -> SlicedPlanes:
        pass

class STLSlicer(Slicer):
    """Slice .stl cad files"""

    def slice_model(self, model: str, height_method: HeightMethod) -> SlicedPlanes:

        mesh = trimesh.load_mesh(model)
        heights = height_method.get_heights(mesh.bounds)
        sections = mesh.section_multiplane([0, 0, 0], [0, 0, 1], heights)
        planes = {}
        for i, section in enumerate(sections):
            if section:
                planes[heights[i]] = MultiPolygon(section.polygons_full)
            else:
                planes[heights[i]] = []

        return SlicedPlanes(planes, mesh.bounds)
