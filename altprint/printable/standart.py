from altprint.printable.base import BasePrint
from altprint.slicer import Slicer
from altprint.layer import Layer, Raster
from altprint.height_method import StandartHeightMethod
from altprint.infill.infill import InfillMethod
from altprint.flow import calculate

class StandartProcess():
    def __init__(self, **kwargs):
        prop_defaults = {
            "position": (100, 100, 0),
            "external_adjust": 0.5,
            "perimeter_num": 2,
            "perimeter_gap": 0.5,
            "raster_gap": 0.5,
            "overlap": 0.0,
            "speed": 2400,
            "flow": calculate()
        }

        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))

class StandartPrint(BasePrint):
    """The common print. Nothing special"""

    _height = float
    _layers_dict = dict[_height, Layer]

    def __init__(self, process: StandartProcess):
        self.process = process
        self.layers: _layers_dict = {}
        self.heights: list[float] = []

    def slice(self, model: str, slicer: Slicer):
        slicer.load_model(model)
        slicer.center_model(self.process.position)
        self.sliced_planes = slicer.slice_model(StandartHeightMethod())
        self.heights = self.sliced_planes.get_heights()

    def make_layers(self, infill_method: InfillMethod):
        for i, height in enumerate(self.heights):
            layer = Layer(self.sliced_planes.planes[height],
                          self.process.perimeter_num,
                          self.process.perimeter_gap,
                          self.process.external_adjust,
                          self.process.overlap)
            layer.make_perimeter(self.process.flow, self.process.speed)
            layer.make_infill_border()
            infill_paths = infill_method.generate_infill(layer,
                                                   self.process.raster_gap,
                                                   90 * (i % 2))
            for path in infill_paths:
                layer.infill.append(Raster(path, self.process.flow, self.process.speed))
            self.layers[height] = layer
