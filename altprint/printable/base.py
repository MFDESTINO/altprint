from abc import ABC, abstractmethod
from altprint.slicer import Slicer
from altprint import flow

class BasePrint(ABC):
    """Base Printable Object"""

    @abstractmethod
    def slice(self):
        pass

    @abstractmethod
    def make_layers(self):
        pass

    @abstractmethod
    def export_gcode(self, filename):
        pass
