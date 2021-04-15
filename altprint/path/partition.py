from shapely.geometry import Polygon
from altprint.path.cgal_bindings.cgal_bindings import y_monotone_partition

def partition_polygons_with_gap(shape, egap, igap):
    eroded_original = shape.buffer(-(egap-igap/2), join_style=2)
    if not eroded_original.exterior.is_ccw:
        eroded_original = Polygon(list(eroded_original.exterior.coords)[::-1])
    partitioned_polygons = y_monotone_partition(eroded_original)
    eroded_partitioned = []
    for polygon in partitioned_polygons:
        p = polygon.buffer(-igap/2, join_style=2)
        if p.area > 0:
            eroded_partitioned.append(p)
    return eroded_partitioned

def partition_shape_with_regions(shape, regions, egap, igap):
    new_shape = list(shape.difference(regions))
    new_shape.extend(regions)
    partitioned = []
    for region in new_shape:
        partitioned.extend(partition_polygons_with_gap(region, egap, igap))
    return partitioned


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from altprint.imports.stl import slice_stl
    from shapely.geometry import MultiPolygon
    ax = plt.subplot()

    planes, translation, heights = slice_stl('models/snap.stl')
    planes2, translation2, heights2 = slice_stl('models/snapstrong.stl', translation=translation)


    shape = planes[0].polygons_full[0]
    regions = MultiPolygon(list(planes2[0].polygons_full))
    partitioned = partition_shape_with_regions(shape, regions, 0, 0.5)

    x, y = shape.exterior.xy
    ax.fill(x, y)


    for i in partitioned:
        x, y = i.exterior.xy
        ax.fill(x, y)
    plt.show()
