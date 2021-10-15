#ifndef __GPSDATA_H__
#define __GPSDATA_H__

#include "../DataStructures/LatLonAlt.h"
#include "../DataStructures/GroundSpeed.h"

struct GPSData {
    uint8_t fix_type;
    LatLonAlt lat_lon_alt;
    uint16_t eph; // GPS HDOP
    uint16_t epv; // GPS VDOP
    uint16_t gps_ground_speed; // cm/s
    GroundSpeed ground_speed;
    uint16_t course_over_ground;
    uint8_t satellites_visible;
    uint16_t vehicle_yaw;
};

#endif // __GPSDATA_H__