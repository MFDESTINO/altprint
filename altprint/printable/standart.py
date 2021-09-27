from altprint.printable.base import BasePrint
from altprint.slicer import Slicer
from altprint.layer import Layer, LayerProcess, Raster
from altprint.height_method import StandartHeightMethod
from altprint.infill.infill import InfillMethod

class StandartPrint(BasePrint):
    """The common print. Nothing special"""

    _height = float
    _layers_dict = dict[_height, Layer]

    def __init__(self):
        self.layers: _layers_dict = {}
        self.heights: list[float] = []

    def slice(self, model: str, slicer: Slicer, table_center=[100, 100, 0]):
        slicer.load_model(model)
        slicer.center_model(table_center)
        self.sliced_planes = slicer.slice_model(StandartHeightMethod())
        self.heights = self.sliced_planes.get_heights()

    def make_layers(self, layer_process: LayerProcess, infill_method: InfillMethod):
        for i, height in enumerate(self.heights):
            layer = Layer(self.sliced_planes.planes[height])
            layer.make_perimeter(layer_process)
            layer.make_infill_border(layer_process)
            infill_paths = infill_method.generate_infill(layer,
                                                   layer_process.gap,
                                                   90 * (i % 2))
            for path in infill_paths:
                layer.infill.append(Raster(path, layer_process))
            self.layers[height] = layer
