#ifndef __GPS_UTILS_H__
#define __GPS_UTILS_H__

#define _USE_MATH_DEFINES
#include <Eigen/Eigen>
#include <cmath>
#include "constants.h"


void ned_to_ecef(double lat0, double lon0, double h0, Eigen::VectorXd& state, double& x, double& y, double& z) {

    double xEast = state[1];
    double yNorth = state[0];
    double zUp = -state[2];

    // Convert to radians in notation consistent with the paper:
    double lambda = lat0 * DEG_TO_RAD;
    double phi = lon0 * DEG_TO_RAD;
    double s = sin(lambda);
    double N = a / sqrt(1 - e_sq * s * s);

    double sin_lambda = sin(lambda);
    double cos_lambda = cos(lambda);
    double cos_phi = cos(phi);
    double sin_phi = sin(phi);

    double x0 = (h0 + N) * cos_lambda * cos_phi;
    double y0 = (h0 + N) * cos_lambda * sin_phi;
    double z0 = (h0 + (1 - e_sq) * N) * sin_lambda;

    double xd = -sin_phi * xEast - cos_phi * sin_lambda * yNorth + cos_lambda * cos_phi * zUp;
    double yd = cos_phi * xEast - sin_lambda * sin_phi * yNorth + cos_lambda * sin_phi * zUp;
    double zd = cos_lambda * yNorth + sin_lambda * zUp;

    x = xd + x0;
    y = yd + y0;
    z = zd + z0;
}

void ecef_to_geodetic(double x, double y, double z,
                                    double& lat, double& lon, double& h)
{
    double p = sqrt(x * x + y * y);
    double q = atan2((z * a), (p * b));
    double sin_q = sin(q);
    double cos_q = cos(q);
    double sin_q_3 = sin_q * sin_q * sin_q;
    double cos_q_3 = cos_q * cos_q * cos_q;
    double phi = atan2((z + eps * b * sin_q_3), (p - e_sq * a * cos_q_3));
    double lambda = atan2(y, x);
    double v = a / sqrt(1.0 - e_sq * sin(phi) * sin(phi));
    
    h = (p / cos(phi)) - v;
    lat = phi * RAD_TO_DEG;
    lon = lambda * RAD_TO_DEG;
}


#endif // __GPS_UTILS_H__