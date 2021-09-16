from abc import ABC, abstractmethod
from altprint.slicer import Slicer
from altprint.layer import Layer, LayerProcess
from altprint.height_method import StandartHeightMethod


class BasePrint(ABC):

    @abstractmethod
    def slice(self):
        pass

    @abstractmethod
    def make_layers(self):
        pass


class StandartPrint(BasePrint):

    _height = float
    _layers_dict = dict[_height, Layer]

    def __init__(self):
        self.layers: _layers_dict = {}
        self.heights: list[float] = []

    def slice(self, model: str, slicer: Slicer):
        self.sliced_planes = slicer.slice_model(model, StandartHeightMethod())
        self.heights = self.sliced_planes.get_heights()

    def make_layers(self, layer_process: LayerProcess):
        for height in self.heights:
            layer = Layer(self.sliced_planes.planes[height])
            layer.make_perimeter(layer_process)
            layer.make_infill_border(layer_process)
            self.layers[height] = layer
