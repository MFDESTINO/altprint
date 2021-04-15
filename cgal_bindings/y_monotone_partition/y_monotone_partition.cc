#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Partition_traits_2.h>
#include <CGAL/partition_2.h>
#include <list>
#include <vector>
#include <iterator>
#include "y_monotone_partition.h"

typedef CGAL::Exact_predicates_inexact_constructions_kernel K;
typedef CGAL::Partition_traits_2<K>                         Traits;
typedef Traits::Point_2                                     Point_2;
typedef Traits::Polygon_2                                   Polygon_2;
typedef std::list<Polygon_2>                                Polygon_list;

std::vector<std::vector<double>> y_monotone_partition(std::vector<double> x_points_in, std::vector<double> y_points_in){
    Polygon_2    polygon;
    Polygon_list partition_polys;
    for (int i=0;i<x_points_in.size();i++){
        polygon.push_back(Point_2(x_points_in[i], y_points_in[i]));
    }

    CGAL::y_monotone_partition_2(polygon.vertices_begin(),
                                    polygon.vertices_end(),
                                    std::back_inserter(partition_polys));

    std::vector<std::vector<double>> final;
    for (auto const& poly : partition_polys)
    {
        std::vector<double> x_points_out;
        std::vector<double> y_points_out;

        for (auto vi=poly.vertices_begin();vi != poly.vertices_end(); ++vi)
        {
            double x = CGAL::to_double((*vi).x());
            double y = CGAL::to_double((*vi).y());
            x_points_out.push_back(x);
            y_points_out.push_back(y);

        }
        final.push_back(x_points_out);
        final.push_back(y_points_out);
    }
    return final;

}
