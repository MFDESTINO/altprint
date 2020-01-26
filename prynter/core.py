from prynter.path.contour import contour
from shapely.geometry import LineString
from shapely import affinity


class Layer:
    def __init__(self, **kwargs):
        prop_defaults = {
            "border": None,
            "height": 0.2,
            "gap": 0.5,
            "perimeters_num": 2,
            "perimeters": [],
            "infill": []
        }

        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))

        for i in range(self.perimeters_num):
            self.perimeters.append(contour(self.border, - self.gap * i))

        self.inner_border = contour(self.border,
                                    - self.gap * self.perimeters_num)

    def translate(self, x, y):
        self.border = affinity.translate(self.border, x, y)

        for i in range(self.perimeters_num):
            self.perimeters[i] = affinity.translate(self.perimeters[i], x, y)

        for i in range(len(self.infill)):
            self.infill[i] = affinity.translate(self.infill[i], x, y)

        self.inner_border = affinity.translate(self.inner_border, x, y)
