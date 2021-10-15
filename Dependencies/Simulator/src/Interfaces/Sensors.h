#ifndef __SENSORS_H__
#define __SENSORS_H__

#include <Eigen/Eigen>
#include "../DataStructures/LatLonAlt.h"
#include "../DataStructures/GroundSpeed.h"
#include "../DataStructures/GPSData.h"

class Sensors {
public:
    ~Sensors() {};
    // State getters
    virtual Eigen::Vector3d get_earth_frame_position() = 0;
    virtual Eigen::Vector3d get_body_frame_velocity() = 0;
    virtual Eigen::Vector3d get_earth_frame_attitude() = 0;
    virtual Eigen::Vector3d get_body_frame_gyro() = 0;
    // Dx state getters
    virtual Eigen::Vector3d get_earth_frame_velocity() = 0;
    virtual Eigen::Vector3d get_body_frame_acceleration() = 0;
    virtual Eigen::Vector3d get_earth_frame_angle_rates() = 0;
    virtual Eigen::Vector3d get_body_frame_angular_acceleration() = 0;
    // --
    virtual Eigen::Vector3d get_magnetic_field() = 0;
    virtual double get_pressure() = 0;
    virtual GPSData get_gps_data() = 0;
    virtual LatLonAlt get_lat_lon_alt() = 0;
    /**
     * Yaw of vehicle relative to Earth's North, zero means not available, use 36000 for north
     * TODO: Make sure that the 6DOF does not spit out 0 for NORTH oriented vehicle
     * (0 in PX4 represents no-yaw info)
     * return yaw in [cDeg]
     */
    virtual uint16_t get_yaw_wrt_earth_north() = 0;
    virtual uint16_t get_course_over_ground() = 0;
    /**
     *  Simulation airspeed + opposite of velocity vector.
     *  Windspeed should be acquired in [cm/s]
     */
    virtual uint16_t get_true_wind_speed() = 0;

    /**
     * Ground speed (lat. , lon. , alt.) in m/s
     */
    virtual Eigen::Vector3d get_absolute_ground_speed() = 0;
    
    virtual bool new_gps_data() = 0;
    // Environment wind in m/s
    virtual Eigen::Vector3d get_environment_wind() = 0;
    // Temperature in [degC]
    virtual double get_environment_temperature() = 0;
};


#endif // __SENSORS_H__