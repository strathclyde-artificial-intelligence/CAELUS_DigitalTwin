#ifndef __DRONESTATE_H__
#define __DRONESTATE_H__

#include "../Helpers/magnetic_field_lookup.h"
#include "../Logging/ConsoleLogger.h"
#include "Sensors.h"
#include "../Helpers/rotation_utils.h"
#include "../Helpers/rotationMatrix.h"
#include "../DataStructures/LatLonAlt.h"
#include "../DataStructures/GPSData.h"
#include "../DataStructures/GroundSpeed.h"
#include <random>
#include <algorithm>
#include <assert.h> 
#include <cmath>
#include <boost/chrono.hpp>
#include <Eigen/Eigen>
#include <mavlink.h>

// #define HIL_STATE_QUATERNION_VERBOSE
// #define HIL_SENSOR_VERBOSE
// #define HIL_GPS_VERBOSE
// #define ASSERT_NOT_NAN

class DroneStateEncoder {
private:
    // Standard deviations for sensor noise
    float noise_Acc = 0.001f;
    float noise_Gps = 10.0f;
    float noise_Gyo = 0.001f;
    float noise_Mag = 0.000001f;
    float noise_Prs = 0.001f;

    double random_walk_gps_x = 0;
    double random_walk_gps_y = 0;
    double random_walk_gps_z = 0;
    double gps_correlation_time = 30.0;

    std::random_device rd; 
    std::mt19937 gen{rd()}; 

    std::normal_distribution<double> nd_acc{0, noise_Acc};
    std::normal_distribution<double> nd_gyo{0, noise_Gyo};
    std::normal_distribution<double> nd_mag{0, noise_Mag};
    std::normal_distribution<double> nd_prs{0, noise_Prs};
    std::normal_distribution<double> nd_gps{0, noise_Gps};

    void update_random_walk_gps(boost::chrono::microseconds us) {
        double dt = (us.count() / 1000000.0);
        double sqrtDt = sqrt(dt);
        double noiseX = sqrtDt * this->nd_gps(this->gen);
        double noiseY = sqrtDt * this->nd_gps(this->gen);
        double noiseZ = sqrtDt * this->nd_gps(this->gen);

        this->random_walk_gps_x += noiseX * dt - this->random_walk_gps_x / gps_correlation_time;
        this->random_walk_gps_y += noiseY * dt - this->random_walk_gps_y / gps_correlation_time;
        this->random_walk_gps_z += noiseZ * dt - this->random_walk_gps_z / gps_correlation_time;
    }

    mavlink_message_t _battery_status_msg(
            uint8_t system_id,
            uint8_t component_id,
            uint8_t battery_id,
            uint8_t  battery_function,
            uint8_t battery_type,
            int16_t battery_temperature,
            uint16_t battery_voltage,
            int16_t current,
            int32_t current_consumed,
            int32_t energy_consumed,
            int8_t battery_remaining_percent
        ) {
            mavlink_message_t msg;
            const uint16_t voltages[10] = {battery_voltage, UINT16_MAX, UINT16_MAX, UINT16_MAX, UINT16_MAX, UINT16_MAX, UINT16_MAX, UINT16_MAX, UINT16_MAX, UINT16_MAX};
            const uint16_t additional_voltages[4] = {0, 0, 0, 0};

            mavlink_msg_battery_status_pack(
                system_id,
                component_id, 
                &msg,
                battery_id, 
                battery_function,
                battery_type,
                battery_temperature,
                voltages,
                current,
                current_consumed,
                energy_consumed,
                battery_remaining_percent,
                0,
                0, // MAV_BATTERY_CHARGE_STATE_UNDEFINED
                additional_voltages,
                0,
                0 // no fault
            );
            return msg;
        }

    mavlink_message_t _hil_sensor_msg(
        uint8_t system_id,
        uint8_t component_id,
        float x_acc,
        float y_acc,
        float z_acc,
        float x_gyro,
        float y_gyro,
        float z_gyro,
        float x_mag,
        float y_mag,
        float z_mag,
        float abs_pressure,
        float diff_pressure,
        float pressure_alt,
        float temperature,
        uint32_t fields_updated = 0b1101111111111
    )
    {
        mavlink_message_t msg;

#ifdef HIL_SENSOR_VERBOSE
        printf("[HIL_SENSOR]\n");
        printf("Body frame Acceleration (m/s**2): %f %f %f \n", x_acc, y_acc, z_acc);
        printf("GYRO xyz speed (rad/s): %f %f %f \n", x_gyro, y_gyro, z_gyro);
        printf("Magfield (gauss): %f %f %f \n", x_mag, y_mag, z_mag);
        printf("Absolute pressure (hPa): %f\n", abs_pressure);
        printf("Differential pressure (hPa): %f\n", diff_pressure);
        printf("Alt (m) : %f \n", pressure_alt);
        printf("Temperature (C): %f\n", temperature);
        printf("Sensor bitfield: %d\n", fields_updated);
        printf("Sim time %llu\n", this->get_sim_time());
#endif

#ifdef ASSERT_NOT_NAN
    assert(x_acc == x_acc);
    assert(y_acc == y_acc);
    assert(z_acc == z_acc);
    assert(x_gyro == x_gyro);
    assert(y_gyro == y_gyro);
    assert(z_gyro == z_gyro);
    assert(x_mag == x_mag);
    assert(y_mag == y_mag);
    assert(z_mag == z_mag);
    assert(abs_pressure == abs_pressure);
    assert(diff_pressure == diff_pressure);
    assert(pressure_alt == pressure_alt);
    assert(temperature == temperature);
    assert(fields_updated == fields_updated);
#endif

        mavlink_msg_hil_sensor_pack(
            system_id,
            component_id,
            &msg,
            this->get_sim_time(),
            x_acc,
            y_acc,
            z_acc,
            x_gyro,
            y_gyro,
            z_gyro,
            x_mag,
            y_mag,
            z_mag,
            abs_pressure,
            diff_pressure,
            pressure_alt,
            temperature,
            fields_updated,
            0 // ID
        );

        return msg;
    }

    mavlink_message_t _hil_state_quaternion_msg(
        uint8_t system_id,
        uint8_t component_id,
        float* attitude_quaternion,
        float roll_speed,
        float pitch_speed,
        float yaw_speed,
        int32_t lat,
        int32_t lon, 
        int32_t alt,
        int16_t vx,
        int16_t vy,
        int16_t vz,
        uint16_t indicated_airspeed,
        uint16_t true_airspeed,
        int16_t x_acc,
        int16_t y_acc,
        int16_t z_acc) 
    {
        mavlink_message_t msg;
#ifdef HIL_STATE_QUATERNION_VERBOSE
        Eigen::VectorXd attitude_euler = this->get_sensors().get_earth_frame_attitude();

        printf("[HIL STATE QUATERNION]\n");
        printf("Attitude quaternion: %f %f %f %f \n", attitude_quaternion[0], attitude_quaternion[1], attitude_quaternion[2], attitude_quaternion[3]);
        printf("Attitude euler (rad): roll: %f pitch: %f yaw: %f \n", attitude_euler[0], attitude_euler[1], attitude_euler[2]);
        printf("RPY Speed (rad/s): %f %f %f \n", roll_speed, pitch_speed, yaw_speed);
        printf("Lat Lon Alt (degE7, degE7, mm): %d %d %d \n", lat, lon, alt);
        printf("Ground speed (cm/s): %d %d %d \n", vx, vy, vz);
        printf("Acceleration (mG): %hd %hd %hd \n", x_acc, y_acc, z_acc);
        printf("True air speed (cm/s): %d \n", true_airspeed);
        printf("Indicated air speed (cm/s): %d \n", indicated_airspeed);
        printf("Sim time %llu\n", this->get_sim_time());
#endif

#ifdef ASSERT_NOT_NAN
assert(attitude_quaternion == attitude_quaternion);
assert(roll_speed == roll_speed);
assert(pitch_speed == pitch_speed);
assert(yaw_speed == yaw_speed);
assert(lat == lat);
assert(lon == lon);
assert(alt == alt);
assert(vx == vx);
assert(vy == vy);
assert(vz == vz);
assert(indicated_airspeed == indicated_airspeed);
assert(true_airspeed == true_airspeed);
assert(x_acc == x_acc);
assert(y_acc == y_acc);
assert(z_acc == z_acc);
#endif

        mavlink_msg_hil_state_quaternion_pack(
            system_id,
            component_id,
            &msg,
            this->get_sim_time(),
            attitude_quaternion,
            roll_speed,
            pitch_speed,
            yaw_speed,
            lat,
            lon,
            alt,
            vx,
            vy,
            vz,
            indicated_airspeed,
            true_airspeed,
            x_acc,
            y_acc,
            z_acc
        );
        
        return msg;
    }

protected:

public:
    virtual uint64_t get_sim_time() = 0;
    virtual Sensors& get_sensors() = 0;
    
    virtual Eigen::VectorXd get_state() = 0;
    virtual Eigen::VectorXd get_dx_state() = 0;

    // THIS IS CURRENTLY UNUSED -- Battery is broadcasted from python probe system
    
    mavlink_message_t battery_status_msg(uint8_t system_id, uint8_t component_id) {
        uint8_t battery_id = 0;
        uint8_t battery_function = 1; // MAV_BATTERY_FUNCTION_ALL
        uint8_t battery_type = 3; // MAV_BATTERY_TYPE_LION
        int16_t battery_temperature = 25; // cDegC
        uint16_t battery_voltage = 5000; // mV
        uint8_t battery_remaining_percent = 100;

        return this->_battery_status_msg(
            system_id,
            component_id,
            battery_id,
            battery_function,
            battery_type,
            battery_temperature,
            battery_voltage,
            -1,
            -1, 
            -1,
            battery_remaining_percent
        );
    }

    mavlink_message_t hil_state_quaternion_msg(uint8_t system_id, uint8_t component_id) {
        Sensors& sensors = this->get_sensors();

        Eigen::VectorXd attitude = euler_angles_to_quaternions(sensors.get_earth_frame_attitude());
        float attitude_float[4] = {0};
        for (int i = 0; i < attitude.size(); i++) attitude_float[i] = attitude[i];

        Eigen::Vector3d angle_rates = sensors.get_earth_frame_angle_rates();
        LatLonAlt lat_lon_alt = sensors.get_lat_lon_alt();
        Eigen::Vector3d ground_speed = sensors.get_absolute_ground_speed() * 100; // m to cm
        Eigen::Vector3d body_frame_acc = caelus_fdm::body2earth(this->get_state()) * sensors.get_body_frame_acceleration();
        uint16_t true_wind_speed = sensors.get_true_wind_speed();

        // TODO REMOVE -- ITS A TEST
        float gforce = 9.81;
        // -----

        // (acc / G * 1000) => m/s**2 to mG (milli Gs)
        body_frame_acc[0] = (int16_t)std::round((body_frame_acc[0] / fabs(gforce)) * 1000);
        body_frame_acc[1] = (int16_t)std::round((body_frame_acc[1] / fabs(gforce)) * 1000);
        body_frame_acc[2] = (int16_t)std::round((body_frame_acc[2] / fabs(gforce)) * 1000);

        // std::cout << body_frame_acc[2] << "  " << sensors.get_body_frame_acceleration()[2] << std::endl;

        return this->_hil_state_quaternion_msg(
            system_id,
            component_id,
            attitude_float,
            angle_rates[0],
            angle_rates[1],
            angle_rates[2],
            lat_lon_alt.latitude_deg * 1e7,
            lat_lon_alt.longitude_deg * 1e7,
            lat_lon_alt.altitude_mm,
            ground_speed[0],
            ground_speed[1],
            ground_speed[2],
            true_wind_speed * 100, // m to cm
            true_wind_speed * 100, // m to cm
            body_frame_acc[0],
            body_frame_acc[1],
            -body_frame_acc[2]
        );
    }

    mavlink_message_t hil_sensor_msg(uint8_t system_id, uint8_t component_id) {
        Sensors& sensors = this->get_sensors();
        
        LatLonAlt lat_lon_alt = sensors.get_lat_lon_alt();
        // m/s**2
        Eigen::Vector3d body_frame_acc = sensors.get_body_frame_acceleration();
        body_frame_acc = caelus_fdm::body2earth(this->get_state()) * body_frame_acc;
        body_frame_acc[2] -= G_FORCE;
        body_frame_acc[2] = std::min(body_frame_acc[2], -9.81);
        body_frame_acc = caelus_fdm::earth2body(this->get_state()) * body_frame_acc;

        // rad/s
        Eigen::Vector3d gyro_xyz = sensors.get_body_frame_gyro();
        // gauss
        Eigen::Vector3d magfield = sensors.get_magnetic_field();
        double abs_pressure = sensors.get_pressure() / 100; // Pa to hPa
        double temperature = sensors.get_environment_temperature();
        float diff_pressure = 0;

        return this->_hil_sensor_msg(
            system_id,
            component_id, 
            body_frame_acc[0] + this->nd_acc(this->gen),
            body_frame_acc[1] + this->nd_acc(this->gen),
            body_frame_acc[2] + this->nd_acc(this->gen),
            gyro_xyz[0] + this->nd_gyo(this->gen),
            gyro_xyz[1] + this->nd_gyo(this->gen),
            gyro_xyz[2] + this->nd_gyo(this->gen),
            magfield[0] + this->nd_mag(this->gen),
            magfield[1] + this->nd_mag(this->gen),
            magfield[2] + this->nd_mag(this->gen),
            abs_pressure + this->nd_prs(this->gen) / 100,
            diff_pressure + this->nd_prs(this->gen) / 100,
            -lat_lon_alt.altitude_mm / 1000 + this->nd_prs(this->gen) / 1000 , 
            temperature + this->nd_prs(this->gen)
        );
    }

    mavlink_message_t hil_gps_msg(uint8_t system_id, uint8_t component_id) {
        Sensors& sensors = this->get_sensors();
        mavlink_message_t msg;

        GPSData gps_data = sensors.get_gps_data();
        GroundSpeed gs = gps_data.ground_speed;
        LatLonAlt lat_lon_alt = gps_data.lat_lon_alt;
        
        this->update_random_walk_gps(boost::chrono::microseconds{4000});
        gps_data.lat_lon_alt.latitude_deg += random_walk_gps_x;
        gps_data.lat_lon_alt.longitude_deg += random_walk_gps_y;
        gps_data.lat_lon_alt.altitude_mm += random_walk_gps_z / 1000;

#ifdef HIL_GPS_VERBOSE
        printf("[GPS SENSOR]\n");
        printf("Lon Lat Alt (degE7, degE7, mm): %f %f %f \n", lat_lon_alt.latitude_deg, lat_lon_alt.longitude_deg, lat_lon_alt.altitude_mm);
        printf("EPH EPV (dimensionless): %d %d \n", gps_data.eph, gps_data.epv);
        printf("Ground speed (cm/s): %d %d %d \n", gs.north_speed, gs.east_speed, gs.down_speed);
        printf("GPS ground speed (m/s): %d\n", gps_data.gps_ground_speed);
        printf("Course over ground: %d (x.%f y.%f) \n",  gps_data.course_over_ground, sensors.get_earth_frame_velocity()[0], sensors.get_earth_frame_velocity()[1]);
        printf("Sats visible: %d \n",  gps_data.satellites_visible);
        printf("Vehicle yaw (deg): %d \n",  gps_data.vehicle_yaw);
        printf("Sim time %llu\n", this->get_sim_time());
#endif

#ifdef ASSERT_NOT_NAN
assert(lat_lon_alt.latitude_deg * 1e7 == lat_lon_alt.latitude_deg * 1e7);
assert(lat_lon_alt.longitude_deg * 1e7 == lat_lon_alt.longitude_deg * 1e7);
assert(lat_lon_alt.altitude_mm == lat_lon_alt.altitude_mm);
assert(gps_data.eph == gps_data.eph);
assert(gps_data.epv == gps_data.epv);
assert(gps_data.gps_ground_speed == gps_data.gps_ground_speed);
assert(gs.north_speed == gs.north_speed);
assert(gs.east_speed == gs.east_speed);
assert(gs.down_speed == gs.down_speed);
assert(gps_data.course_over_ground == gps_data.course_over_ground);
assert(gps_data.satellites_visible == gps_data.satellites_visible);
assert(gps_data.vehicle_yaw == gps_data.vehicle_yaw);
#endif

        mavlink_msg_hil_gps_pack(
            system_id,
            component_id,
            &msg,
            this->get_sim_time(),
            3, // 3d fix
            lat_lon_alt.latitude_deg * 1e7,
            lat_lon_alt.longitude_deg * 1e7,
            lat_lon_alt.altitude_mm,
            gps_data.eph,
            gps_data.epv,
            gps_data.gps_ground_speed + this->nd_acc(this->gen),
            gs.north_speed + this->nd_acc(this->gen),
            gs.east_speed + this->nd_acc(this->gen),
            gs.down_speed + this->nd_acc(this->gen),
            gps_data.course_over_ground,
            gps_data.satellites_visible,
            0, // ID
            gps_data.vehicle_yaw
        );

        return msg;
    }

    mavlink_message_t system_time_msg(uint8_t system_id, uint8_t component_id) {
        mavlink_message_t msg;

        uint64_t time_unix_usec = boost::chrono::duration_cast<boost::chrono::microseconds>(boost::chrono::system_clock::now().time_since_epoch()).count();
        uint32_t time_boot_ms = this->get_sim_time() / 1000; // us to ms

        mavlink_msg_system_time_pack(
            system_id,
            component_id,
            &msg,
            time_unix_usec,
            time_boot_ms
        );

        return msg;
    }
};

#endif // __DRONESTATE_H__