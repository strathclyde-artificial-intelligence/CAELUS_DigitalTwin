#ifndef __MAGNETIC_FIELD_LOOKUP_H__
#define __MAGNETIC_FIELD_LOOKUP_H__

#include <Eigen/Eigen>

Eigen::VectorXd magnetic_field_for_latlonalt(const int32_t* lat_lon_alt);

#endif // __MAGNETIC_FIELD_LOOKUP_H__