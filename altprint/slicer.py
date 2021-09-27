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
    def load_model(self, model_file: str):
        pass

    @abstractmethod
    def translate_model(self, translation):
        pass

    @abstractmethod
    def center_model(self, table_center) -> list:
        pass

    @abstractmethod
    def slice_model(self, height_method: HeightMethod) -> SlicedPlanes:
        pass

class STLSlicer(Slicer):
    """Slice .stl cad files"""

    def load_model(self, model_file: str):
        self.model = trimesh.load_mesh(model_file)

    def translate_model(self, translation):
        self.model.apply_translation(translation)

    def center_model(self, table_center) -> list:
        mesh_x, mesh_y, mesh_z = self.model.extents
        mesh_center = self.model.bounds[0] + np.array([mesh_x/2, mesh_y/2, 0])
        table_center = np.array(table_center)
        translation = list(table_center - mesh_center)
        self.model.apply_translation(translation)
        return translation

    def slice_model(self, height_method: HeightMethod, heights = None) -> SlicedPlanes:
        if not heights:
            heights = height_method.get_heights(self.model.bounds)
        sections = self.model.section_multiplane([0, 0, 0], [0, 0, 1], heights)
        planes = {}
        for i, section in enumerate(sections):
            if section:
                planes[heights[i]] = MultiPolygon(list(section.polygons_full))
            else:
                planes[heights[i]] = []

        return SlicedPlanes(planes, self.model.bounds)
