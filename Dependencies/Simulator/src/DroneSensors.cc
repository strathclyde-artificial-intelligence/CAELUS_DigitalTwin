#include "DroneSensors.h"
#include "Interfaces/DynamicObject.h"
#include "DataStructures/LatLonAlt.h"
#include "Helpers/baro_utils.h"
#include "Helpers/gps_utils.h"
#include "Helpers/magnetic_field_lookup.h"
#include "Helpers/rotationMatrix.h"

#define DEG_TO_RAD (M_PI / 180.0)
#define RAD_TO_DEG (180.0 / M_PI)

DroneSensors::DroneSensors(DynamicObject& drone, LatLonAlt gps_origin) : 
    drone(drone),
    gps_origin(gps_origin)
    {}

#pragma mark DRONE_STATE_GETTERS

/**
 * Body frame origin (x,y,z) in NED with respect to earth frame
 */
Eigen::Vector3d DroneSensors::get_earth_frame_position() {
    return this->drone.get_vector_state().segment(0,3);
}

Eigen::Vector3d DroneSensors::get_body_frame_velocity() {
    return this->drone.get_vector_state().segment(3,3);
}

Eigen::Vector3d DroneSensors::get_earth_frame_attitude() {
    return this->drone.get_vector_state().segment(6,3);
}

Eigen::Vector3d DroneSensors::get_body_frame_gyro() {
    return this->drone.get_vector_state().segment(9,3);
}

#pragma mark DRONE_DX_STATE_GETTERS

Eigen::Vector3d DroneSensors::get_earth_frame_velocity() {
    return this->drone.get_vector_dx_state().segment(0,3);
}

Eigen::Vector3d DroneSensors::get_body_frame_acceleration() {
    return this->drone.get_vector_dx_state().segment(3,3);
}

Eigen::Vector3d DroneSensors::get_earth_frame_angle_rates() {
    return this->drone.get_vector_dx_state().segment(6,3);
}

Eigen::Vector3d DroneSensors::get_body_frame_angular_acceleration() {
    return this->drone.get_vector_dx_state().segment(9,3);
}

#pragma mark OTHER_SENSOR_DATA

Eigen::Vector3d DroneSensors::get_magnetic_field() {
    LatLonAlt lLa = this->get_lat_lon_alt();
    Eigen::Vector3d magfield = magnetic_field_for_latlonalt(lLa);
    return caelus_fdm::earth2body(this->drone.get_vector_state()) * magfield;
}

double DroneSensors::get_pressure() {
    LatLonAlt lLa = this->get_lat_lon_alt();
    return alt_to_baro((double)lLa.altitude_mm / 1000.0); // mm to m
}

GPSData DroneSensors::get_gps_data() {
    Eigen::Vector3d ground_speed = this->get_absolute_ground_speed() * 100;
    GroundSpeed gs{static_cast<int16_t>(ground_speed[0]), static_cast<int16_t>(ground_speed[1]), static_cast<int16_t>(ground_speed[2])};

    GPSData data{
        // GPS fix type
        3,
        this->get_lat_lon_alt(),
        // Diluition of position measurements
        // Should smooth overtime from high value to low value
        // to simulate improved measurement accuracy over time.
        // TODO: Implement smoothing (Kalman filter?)
        static_cast<uint16_t>(0.3 * 100),
        static_cast<uint16_t>(0.4 * 100),
        // Horizontal ground speed
        static_cast<uint16_t>(sqrt(pow(ground_speed[0], 2) + pow(ground_speed[1], 2))),
        gs,
        this->get_course_over_ground(),
        10,
        this->get_yaw_wrt_earth_north()
    };

    return data;
}

uint16_t DroneSensors::get_yaw_wrt_earth_north() {
    Eigen::Vector3d attitude = this->get_earth_frame_attitude();
    double yaw_deg = RAD_TO_DEG*attitude[2];
    double offset = fmod(yaw_deg, 360) < 0 ? 360.0 : 0.0;
    return (static_cast<uint16_t>(fmod(yaw_deg, 360) + offset) + 1) % 361;
}

uint16_t DroneSensors::get_course_over_ground() {
    Eigen::VectorXd xyz_dot = this->get_earth_frame_velocity();
    // Maybe convert xyz to earth frame?
    double angle = atan2(xyz_dot[1], xyz_dot[0]);
    angle = angle < 0 ? angle + 2*M_PI : angle;
    return fmod(RAD_TO_DEG * (angle), 360) * 100; // Deg => cDeg
}

Eigen::Vector3d DroneSensors::get_environment_wind() {
    return Eigen::VectorXd::Zero(3);
}

double DroneSensors::get_environment_temperature() {
    return 25;
}

/**
 * Ground speed (lat. , lon. , alt.) in m/s
 */
Eigen::Vector3d DroneSensors::get_absolute_ground_speed() {
    Eigen::Vector3d earth_frame_velocity = this->get_earth_frame_velocity();
    // TODO: FIND CONVERSION BETWEEN THOSE COORDS TO GROUND SPEED
    return earth_frame_velocity;
}

uint16_t DroneSensors::get_true_wind_speed() {
    Eigen::Vector3d ground_speed_vec = this->get_absolute_ground_speed();
    return (ground_speed_vec * -1).norm();
}

/**
 * lat: [degE7]
 * lon: [degE7]
 * alt: [mm]
 */
LatLonAlt DroneSensors::get_lat_lon_alt() {
    LatLonAlt lLa;

    Eigen::VectorXd state = this->drone.get_vector_state();
    double lat_lon_alt[3] = {0};

    ned_to_ecef(
        this->gps_origin.latitude_deg,
        this->gps_origin.longitude_deg,
        this->gps_origin.altitude_mm / 1000,
        state,
        lat_lon_alt[0],
        lat_lon_alt[1],
        lat_lon_alt[2]
    );

    ecef_to_geodetic(
        lat_lon_alt[0],
        lat_lon_alt[1],
        lat_lon_alt[2],
        lat_lon_alt[0],
        lat_lon_alt[1],
        lat_lon_alt[2]
    );        

    lLa.latitude_deg = lat_lon_alt[0];
    lLa.longitude_deg = lat_lon_alt[1];
    lLa.altitude_mm = lat_lon_alt[2] * 1000; // m to mm

    return lLa;
}

bool DroneSensors::new_gps_data() {
    return true;
}
