#ifndef __MAGNETIC_FIELD_LOOKUP_H__
#define __MAGNETIC_FIELD_LOOKUP_H__

#include <Eigen/Eigen>
#include "../DataStructures/LatLonAlt.h"

Eigen::VectorXd magnetic_field_for_latlonalt(LatLonAlt lat_lon_alt);

#endif // __MAGNETIC_FIELD_LOOKUP_H__