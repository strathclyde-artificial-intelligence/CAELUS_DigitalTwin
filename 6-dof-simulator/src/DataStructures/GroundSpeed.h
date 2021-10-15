#ifndef __GROUNDSPEED_H__
#define __GROUNDSPEED_H__

// Measurements in earth-fixed NED frame
struct GroundSpeed {
    int16_t north_speed;
    int16_t east_speed;
    int16_t down_speed;
};

#endif // __GROUNDSPEED_H__