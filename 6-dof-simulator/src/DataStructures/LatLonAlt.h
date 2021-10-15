#ifndef __LATLONALT_H__
#define __LATLONALT_H__

// WGS84 earth model
struct LatLonAlt {
    double latitude_deg;
    double longitude_deg;
    double altitude_mm; // MSL (POSITIVE UP)
};

#endif // __LATLONALT_H__