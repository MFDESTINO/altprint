from abc import ABC, abstractmethod

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
