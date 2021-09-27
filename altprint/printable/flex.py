from altprint.printable.base import BasePrint
from altprint.slicer import Slicer
from altprint.layer import Layer, LayerProcess, Raster
from altprint.height_method import StandartHeightMethod
from altprint.infill.infill import InfillMethod
from altprint.lineutil import split_by_regions

class FlexPrint(BasePrint):
    """The common print. Nothing special"""

    _height = float
    _layers_dict = dict[_height, Layer]

    def __init__(self):
        self.layers: _layers_dict = {}
        self.heights: list[float] = []

    def slice(self, model: str, flex_model: str, slicer: Slicer, table_center=[100, 100, 0]):
        slicer.load_model(model)
        translation = slicer.center_model(table_center)
        self.sliced_planes = slicer.slice_model(StandartHeightMethod())
        self.heights = self.sliced_planes.get_heights()

        slicer.load_model(flex_model)
        slicer.translate_model(translation)
        self.flex_planes = slicer.slice_model(StandartHeightMethod(), self.heights)

    def make_layers(self, layer_process: LayerProcess, flex_process: LayerProcess, infill_method: InfillMethod):
        for i, height in enumerate(self.heights):
            layer = Layer(self.sliced_planes.planes[height])
            layer.make_perimeter(layer_process)
            layer.make_infill_border(layer_process)
            infill_paths = infill_method.generate_infill(layer,
                                                         layer_process.gap,
                                                         0)
            flex_regions = self.flex_planes.planes[height]
            infill_paths = split_by_regions(infill_paths, flex_regions)

            for path in infill_paths:
                flex_path = False
                for region in flex_regions:
                    if path.within(region):
                        layer.infill.append(Raster(path, flex_process))
                        flex_path = True
                        break
                if not flex_path:
                    layer.infill.append(Raster(path, layer_process))

            self.layers[height] = layer
