#ifndef __DRONESENSORS_H__
#define __DRONESENSORS_H__

#include "Interfaces/Sensors.h"
#include "Interfaces/DynamicObject.h"
#include "Interfaces/TimeHandler.h"

class DroneSensors : public Sensors {
    
protected:
    DynamicObject& drone;
    LatLonAlt gps_origin;
public:
    DroneSensors(DynamicObject& drone, LatLonAlt gps_origin);
    ~DroneSensors() {};
    Eigen::Vector3d get_earth_frame_position() override;
    Eigen::Vector3d get_body_frame_velocity() override;
    Eigen::Vector3d get_earth_frame_attitude() override;
    Eigen::Vector3d get_body_frame_gyro() override;
    Eigen::Vector3d get_earth_frame_velocity() override;
    Eigen::Vector3d get_body_frame_acceleration() override;
    Eigen::Vector3d get_earth_frame_angle_rates() override;
    Eigen::Vector3d get_body_frame_angular_acceleration() override;
    Eigen::Vector3d get_magnetic_field() override;
    double get_pressure() override;
    GPSData get_gps_data() override;
    LatLonAlt get_lat_lon_alt() override;
    uint16_t get_yaw_wrt_earth_north() override;
    uint16_t get_course_over_ground() override;
    bool new_gps_data() override;
    Eigen::Vector3d get_environment_wind() override;
    uint16_t get_true_wind_speed() override;
    Eigen::Vector3d get_absolute_ground_speed() override;
    double get_environment_temperature() override;
};

#endif // __DRONESENSORS_H__