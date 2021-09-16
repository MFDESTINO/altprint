from abc import ABC, abstractmethod
from shapely.geometry import MultiLineString
from altprint.layer import Layer

class InfillMethod(ABC):

    @abstractmethod
    def generate_infill(self, layer: Layer) -> MultiLineString:
        pass
