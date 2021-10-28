from abc import ABC, abstractmethod
import numpy as np


class HeightMethod(ABC):
    """Generates the height values on which the object will be sliced in"""

    @abstractmethod
    def get_heights(self, bounds) -> list[float]:
        pass

class StandartHeightMethod(HeightMethod):
    """Evenly spaced layers"""

    def __init__(self, layer_height: float = 0.2):
        self.layer_height = layer_height

    def get_heights(self, bounds) -> list[float]:
        zi = bounds[0][2]
        zf = bounds[1][2]
        h = zf - zi
        heights = list(np.linspace(zi, zf, round(h/self.layer_height)+1))
        heights[-1] = heights[-1]-0.001 #numerical adjust to make the slicer include the last layer
        heights = list(np.around(heights, decimals=3))
        return heights
