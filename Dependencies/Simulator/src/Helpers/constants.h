#ifndef __CONSTANTS_H__
#define __CONSTANTS_H__

const double G_FORCE = 9.81;
const double K_Pb = 101325.0;  // static pressure at sea level [Pa]
const double K_Tb = 288.15;    // standard temperature at sea level [K]
const double K_Lb = -0.0065;   // standard temperature lapse rate [K/m]
const double K_M = 0.0289644;  // molar mass of Earth's air [kg/mol]
const double K_R = 8.31432;    // universal gas constant

// WGS-84 geodetic constants
const double a = 6378137.0;         // WGS-84 Earth semimajor axis (m)
const double b = 6356752.31414036;     // Derived Earth semiminor axis (m)
const double f = (a - b) / a;           // Ellipsoid Flatness
const double f_inv = 1.0 / f;       // Inverse flattening
const double a_sq = a * a;
const double b_sq = b * b;
const double e_sq = f * (2 - f);    // Square of Eccentricity
const double eps = e_sq / (1.0 - e_sq);

#define DEG_TO_RAD (M_PI / 180.0)
#define RAD_TO_DEG (180.0 / M_PI)

#endif // __CONSTANTS_H__