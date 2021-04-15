%module y_monotone_partition
%{
        #include "y_monotone_partition.h"
%}

%include "std_vector.i"
// Instantiate templates used by example
namespace std {
   %template(DoubleVector) vector<double>;
   %template(VectorVector) vector<vector<double>>;
}


%include "y_monotone_partition.h"
