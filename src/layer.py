from src.genpath import gen_square, contour
from shapely.geometry import LineString, LinearRing, MultiLineString, Point, MultiPoint, Polygon
from shapely import affinity

class Layer:
    def __init__(self, shape, out_adj, perimeters_num, gap, bed, angle):
        self.perimeters = []
        self.inner_shape = []
        self.shape = contour(shape, out_adj)
        self.out_adj = out_adj
        self.perimeters_num = perimeters_num
        self.gap = gap
        self.angle = angle
        self.inner_shape.append(gen_square(contour(self.shape,
            - self.gap * self.perimeters_num), self.gap, self.angle))

        for i in range(self.perimeters_num):
            self.perimeters.append(LinearRing(contour(self.shape, - self.gap * i)))

        self.inner_shape = MultiLineString(self.inner_shape)
        self.perimeters = MultiLineString(self.perimeters)
        self.bounds = [self.perimeters.bounds[2] - self.perimeters.bounds[0],
                       self.perimeters.bounds[3] - self.perimeters.bounds[1]]

    def translate(self, dx, dy):
        self.inner_shape = affinity.translate(self.inner_shape, dx, dy)
        self.perimeters = affinity.translate(self.perimeters, dx, dy)
