from abc import ABC, abstractmethod
from altprint.slicer import Slicer
from altprint.layer import Layer, LayerProcess
from altprint.height_method import StandartHeightMethod
from altprint.infill.infill import InfillMethod
from altprint.infill.rectilinear_optimal import RectilinearOptimal

class BasePrint(ABC):
    """Base Printable Object"""

    @abstractmethod
    def slice(self):
        pass

    @abstractmethod
    def make_layers(self):
        pass


class StandartPrint(BasePrint):
    """The common print. Nothing special"""

    _height = float
    _layers_dict = dict[_height, Layer]

    def __init__(self):
        self.layers: _layers_dict = {}
        self.heights: list[float] = []

    def slice(self, model: str, slicer: Slicer, table_center = [100,100,0]):
        slicer.load_model(model)
        slicer.center_model(table_center)
        self.sliced_planes = slicer.slice_model(StandartHeightMethod())
        self.heights = self.sliced_planes.get_heights()

    def make_layers(self, layer_process: LayerProcess, infill_method: InfillMethod):
        for height in self.heights:
            layer = Layer(self.sliced_planes.planes[height])
            layer.make_perimeter(layer_process)
            layer.make_infill_border(layer_process)
            layer.infill = infill_method.generate_infill(layer, 0.5, 0)
            self.layers[height] = layer
