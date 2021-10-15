#ifndef __BARO_UTILS_H__
#define __BARO_UTILS_H__

#define _USE_MATH_DEFINES
#include "constants.h"
#include <cmath>

// Ripped from JMavSim
/**
 * Convert altitude to barometric pressure
 * @param alt        Altitude in meters
 * @return Barometric pressure in Pa
 */
double alt_to_baro(double alt) {
    if (alt <= 11000.0) {
        return K_Pb * std::pow(K_Tb / (K_Tb + (K_Lb * alt)), (G_FORCE * K_M) / (K_R * K_Lb));
    } else if (alt <= 20000.0) {
        double f = 11000.0;
        double a = alt_to_baro(f);
        double c = K_Tb + (f * K_Lb);
        return a * std::pow(M_E, ((-G_FORCE) * K_M * (alt - f)) / (K_R * c));
    }
    return 0.0;
}


#endif // __BARO_UTILS_H__