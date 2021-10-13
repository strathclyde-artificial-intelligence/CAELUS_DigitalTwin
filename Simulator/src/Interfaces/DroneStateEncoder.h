#ifndef __DRONESTATE_H__
#define __DRONESTATE_H__

#include "../Helpers/magnetic_field_lookup.h"
#include "../Logging/ConsoleLogger.h"
#include <cmath>
#include <boost/chrono.hpp>
#include <Eigen/Eigen>
#include <mavlink.h>
#include <EquationsOfMotion/rotationMatrix.h>
#include <random>

// #define HIL_STATE_QUATERNION_VERBOSE
#define HIL_SENSOR_VERBOSE
// #define HIL_GPS_VERBOSE

class DroneStateEncoder {
protected:

    float noise_Acc = 0.005f;
    float noise_Gyo = 0.001f;
    float noise_Mag = 0.0005f;
    float noise_Prs = 0.0001f;

    uint32_t baro_throttle_counter = 0;

#define G_FORCE 9.81
#define K_Pb 101325.0  // static pressure at sea level [Pa]
#define K_Tb 288.15    // standard temperature at sea level [K]
#define K_Lb -0.0065   // standard temperature lapse rate [K/m]
#define K_M 0.0289644  // molar mass of Earth's air [kg/mol]
#define K_R 8.31432    // universal gas constant

    std::default_random_engine generator;

    double randomNoise(float stdDev) {
        std::normal_distribution<double> dist(0, stdDev);
        double n = dist(generator);
        return n;
    }

    void add_noise(Eigen::VectorXd vec, float stdDev) {
        for (int i = 0; i < vec.size(); i++) {
            vec[i] + randomNoise(stdDev);
        }
    }

    // Ripped from JMavSim
    /**
     * Convert altitude to barometric pressure
     * @param alt        Altitude in meters
     * @return Barometric pressure in Pa
     */
    static double alt_to_baro(double alt) {
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

    static void euler_to_quaterions(const float* euler_rpy, float* quaternion) {
        float roll = euler_rpy[0];
        float pitch = euler_rpy[1];
        float yaw = euler_rpy[2];
        // Order should be w x y z 
        quaternion[1] = sin(roll/2) * cos(pitch/2) * cos(yaw/2) - cos(roll/2) * sin(pitch/2) * sin(yaw/2);
        quaternion[2] = cos(roll/2) * sin(pitch/2) * cos(yaw/2) + sin(roll/2) * cos(pitch/2) * sin(yaw/2);
        quaternion[3] = cos(roll/2) * cos(pitch/2) * sin(yaw/2) - sin(roll/2) * sin(pitch/2) * cos(yaw/2);
        quaternion[0] = cos(roll/2) * cos(pitch/2) * cos(yaw/2) + sin(roll/2) * sin(pitch/2) * sin(yaw/2);
    }
    
    void get_attitude(float* attitude) { // <float(4)>
        Eigen::VectorXd& state = this->get_vector_state();
        float euler[3] = {0};
        for (uint i = 0; i < 3; i++) euler[i] = state[6+i];
        DroneStateEncoder::euler_to_quaterions((const float*)euler, attitude);
    } 

    void get_rpy_speed(float* rpy) { // <float(3)>
        Eigen::VectorXd state = this->get_vector_state();
        for (uint i = 0; i < 3; i++) *(rpy+i) = state[i + 9];
    }

    /**
     * Ground speed (lat. , lon. , alt.) in cm/s
     */
    void get_ground_speed(int16_t* x_y_z) { // <int16_t(3)>
        Eigen::VectorXd state_derivative = this->get_vector_dx_state();
        for (uint i = 0; i < 3; i++) x_y_z[i] = state_derivative[i];
        x_y_z[0] *= 100;
        x_y_z[1] *= 100;
        x_y_z[2] *= 100;
    } 
    
    /**
     * Body frame (NED) acceleration (ẍ , ÿ , z̈) in m/s**2
     */
    void get_body_frame_acceleration(float* x_y_z) { // <float(3)>
        Eigen::VectorXd state_derivative = this->get_vector_dx_state();
        for (uint i = 0; i < 3; i++) *(x_y_z+i) = state_derivative[3 + i];
    } 

    /**
     * Body frame origin (x,y,z) in NED with respect to earth frame
     */
    void get_body_frame_origin(float* x_y_z) { // <float(3)>
        Eigen::VectorXd state = this->get_vector_state();
        for (uint i = 0; i < 3; i++) *(x_y_z+i) = state[i];
    }
    
    void get_earth_fixed_velocity(int16_t* xyz) { //<int16_t(3)>
        
        Eigen::VectorXd state = this->get_vector_state();
        Eigen::VectorXd xyz_dot_body_frame = state.segment(3,3);

        Eigen::MatrixXd body_to_earth_rot = caelus_fdm::body2earth(state);
        Eigen::VectorXd earth_frame_velocity = body_to_earth_rot * xyz_dot_body_frame;

        for (uint i = 0; i < 3; i++) *(xyz+i) = earth_frame_velocity[i];
    }   

    #define DEG_TO_RAD (M_PI / 180.0)
    #define RAD_TO_DEG (180.0 / M_PI)

    void ned_to_ecef(double lat0, double lon0, double h0, Eigen::VectorXd& state, double& x, double& y, double& z) {
        // WGS-84 geodetic constants
        const double a = 6378137.0;         // WGS-84 Earth semimajor axis (m)

        const double b = 6356752.31414036;     // Derived Earth semiminor axis (m)
        const double f = (a - b) / a;           // Ellipsoid Flatness
        const double f_inv = 1.0 / f;       // Inverse flattening

        //const double f_inv = 298.257223563; // WGS-84 Flattening Factor of the Earth 
        //const double b = a - a / f_inv;
        //const double f = 1.0 / f_inv;

        const double a_sq = a * a;
        const double b_sq = b * b;
        const double e_sq = f * (2 - f);    // Square of Eccentricity

        double xEast = state[0];
        double yNorth = state[1];
        // double zUp = -1 * state[2];
        double zUp = state[2];

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
        // WGS-84 geodetic constants
        const double a = 6378137.0;         // WGS-84 Earth semimajor axis (m)

        const double b = 6356752.31414036;     // Derived Earth semiminor axis (m)
        const double f = (a - b) / a;           // Ellipsoid Flatness
        const double f_inv = 1.0 / f;       // Inverse flattening

        const double a_sq = a * a;
        const double b_sq = b * b;
        const double e_sq = f * (2 - f); 
        double eps = e_sq / (1.0 - e_sq);
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

    /**
     * lat: [degE7]
     * lon: [degE7]
     * alt: [mm]
     */
    void get_lat_lon_alt(int32_t* lat_lon_alt) {  // <int32_t(3)>
    
// Glasgow LatLon Height
#define INITIAL_LAT 55.8609825
#define INITIAL_LON -4.2488787
#define INITIAL_ALT 26

        Eigen::VectorXd state = this->get_vector_state();
        double d_lat_lon_alt[3] = {0};

        ned_to_ecef(INITIAL_LAT, INITIAL_LON, INITIAL_ALT, state, d_lat_lon_alt[0], d_lat_lon_alt[1], d_lat_lon_alt[2]);
        ecef_to_geodetic(d_lat_lon_alt[0], d_lat_lon_alt[1], d_lat_lon_alt[2], d_lat_lon_alt[0], d_lat_lon_alt[1], d_lat_lon_alt[2]);        

        lat_lon_alt[0] = (int32_t)(d_lat_lon_alt[0] * 1e7);
        lat_lon_alt[1] = (int32_t)(d_lat_lon_alt[1] * 1e7);
        lat_lon_alt[2] = (int32_t)((d_lat_lon_alt[2] * 1000)); // m to mm
        
    }
    
    /**
     *  Simulation airspeed + opposite of velocity vector.
     *  Windspeed should be acquired in [cm/s]
     */
    void get_true_wind_speed(uint16_t* wind_speed) { // <uint16_t(1)>
        
        int16_t ground_speed[3] = {0};
        this->get_ground_speed((int16_t*)ground_speed);   

        Eigen::Vector3d ground_speed_vec{3};
        for (uint i = 0; i < sizeof(ground_speed) / sizeof(int16_t); i++)
            ground_speed_vec[i] = ground_speed[i];

        // Environment wind is assumed to be in m/s -- cm/s is required.
        Eigen::Vector3d environment_wind = this->get_environment_wind() * 100; 
        Eigen::Vector3d cumulative_wind = (ground_speed_vec + environment_wind) * -1;
        double wind_magnitude = cumulative_wind.norm();
        *wind_speed = (uint16_t)wind_magnitude;
    }

    /**
     * Vehicle course-over-ground in [cDeg]
     */
    void get_course_over_ground(uint16_t* cog) { // <uint16_t(1)>
        Eigen::VectorXd state = this->get_vector_state();
        float xyz_dot[3] = {0};
        for (uint i = 0; i < 3; i++) *(xyz_dot+i) = state[i + 3];
        // Maybe convert xyz to earth frame?
        *cog = ((atan2(xyz_dot[0], xyz_dot[1]) * 180) / M_PI) * 100; // Deg => cDeg
    }

    /**
     * Yaw of vehicle relative to Earth's North, zero means not available, use 36000 for north
     * TODO: Make sure that the 6DOF does not spit out 0 for NORTH oriented vehicle
     * (0 in PX4 represents no-yaw info)
     * return yaw in [cDeg]
     */
    void get_vehicle_yaw_wrt_earth_north(uint16_t* yaw) { // <uint16_t(1)>
        Eigen::VectorXd state = this->get_vector_state();
        ConsoleLogger* logger = ConsoleLogger::shared_instance();
        *yaw = (uint16_t)std::round((((state[8]) * 180) / M_PI) * 100);

        if (*yaw == 0) {
            // logger->debug_log("[Warning] YAW is ZERO -- PX4 will interpret this as no-yaw!");
            // logger->debug_log("[Warning] Setting yaw to 1°...");
            *yaw += 1;
        }
    }

public:
    virtual uint64_t get_sim_time() = 0;
    // Environment wind in m/s
    virtual Eigen::Vector3d get_environment_wind() = 0;
    // Temperature in [degC]
    virtual float get_temperature_reading() = 0;

    /**
     * Drone state as populated by the CAELUS_FDM package.
     * <
     *  x , y , z    [0:3]  vehicle origin with respect to earth-frame (NED m) (ENU when earth)
     *  u, v, w      [3:6]  body-frame velocity (m/s)
     *  ɸ , θ , ѱ    [6:9]  (roll, pitch, yaw) body-frame orientation with respect to earth-frame (rad)
     *  p, q, r      [9:12] (roll., pitch., yaw.) body-frame orientation velocity (rad/s)
     * >
     */
    virtual Eigen::VectorXd& get_vector_state() = 0;
    /**
     *  (FixedWingEOM.h:evaluate)
     *  Drone state derivative as populated by the CAELUS_FDM package.
     *  ẋ , ẏ , ż       [0:3]  earth-frame velocity (NED)
     *  u., v., w.      [3:6]  body-frame acceleration (m/s**2)
     *  ɸ. , θ. , ѱ.    [6:9]  earth-frame angle rates (Euler rates)
     *  p. , q. , r.    [9:12] body-frame angular rates (What unit?)
     */
    virtual Eigen::VectorXd& get_vector_dx_state() = 0;
    
    mavlink_message_t hil_state_quaternion_msg(uint8_t system_id, uint8_t component_id) {
        mavlink_message_t msg;
        float attitude[4] = {0};
        float rpy_speed[3] = {0};
        int32_t lat_lon_alt[3] = {0};
        int16_t ground_speed[3] = {0};
        float f_acceleration[3] = {0};
        int16_t acceleration[3] = {0};
        uint16_t true_wind_speed = 0;

        this->get_attitude((float*)attitude);
        this->get_rpy_speed((float*)rpy_speed);
        this->get_lat_lon_alt((int32_t*)lat_lon_alt);
        this->get_ground_speed((int16_t*)ground_speed);
        this->get_body_frame_acceleration((float*)f_acceleration);
        this->get_true_wind_speed(&true_wind_speed);

        // (acc / G * 1000) => m/s**2 to mG (milli Gs)
        acceleration[0] = (int16_t)std::round((f_acceleration[0] / fabs(G_FORCE)) * 1000);
        acceleration[1] = (int16_t)std::round((f_acceleration[1] / fabs(G_FORCE)) * 1000);
        acceleration[2] = (int16_t)std::round((f_acceleration[2] / fabs(G_FORCE)) * 1000);

#ifdef HIL_STATE_QUATERNION_VERBOSE
        Eigen::VectorXd& state = this->get_vector_state();
        float attitude_euler[3] = {0};
        for (uint i = 0; i < 3; i++) attitude_euler[i] = state[6+i];

        printf("[HIL STATE QUATERNION]\n");
        printf("Attitude quaternion: %f %f %f %f \n", attitude[0], attitude[1], attitude[2], attitude[3]);
        printf("Attitude euler (rad): roll: %f pitch: %f yaw: %f \n", attitude_euler[0], attitude_euler[1], attitude_euler[2]);
        printf("RPY Speed (rad/s): %f %f %f \n", rpy_speed[0], rpy_speed[1], rpy_speed[2]);
        printf("Lat Lon Alt (degE7, degE7, mm): %d %d %d \n", lat_lon_alt[0], lat_lon_alt[1], lat_lon_alt[2]);
        printf("Ground speed (m/s): %d %d %d \n", ground_speed[0] / 100, ground_speed[1] / 100, ground_speed[2] / 100);
        printf("Acceleration (mG): %d %d %d \n", acceleration[0], acceleration[1], acceleration[2]);
        printf("True wind speed (m/s): %d \n", true_wind_speed / 100);
        printf("Sim time %llu\n", this->get_sim_time());
#endif


        mavlink_msg_hil_state_quaternion_pack(
            system_id,
            component_id,
            &msg,
            this->get_sim_time(),
            (float*)attitude,
            rpy_speed[0], 
            rpy_speed[1],
            rpy_speed[2],
            lat_lon_alt[0],
            lat_lon_alt[1],
            lat_lon_alt[2],
            ground_speed[0],
            ground_speed[1],
            ground_speed[2],
            true_wind_speed,
            true_wind_speed,
            acceleration[0],
            acceleration[1],
            acceleration[2]
        );

        return msg;
    }

    mavlink_message_t hil_sensor_msg(uint8_t system_id, uint8_t component_id) {
        mavlink_message_t msg;
        
        int32_t lat_lon_alt[3] = {0};
        float drone_x_y_z[3] = {0};
        float body_frame_acc[3] = {0}; // m/s**2
        float gyro_xyz[3] = {0}; // rad/s
        float magfield[3] = {0}; // gauss
        float abs_pressure = 0; // hPa
        float diff_pressure = 0;

        this->get_body_frame_acceleration((float*)body_frame_acc);
        this->get_rpy_speed((float*) gyro_xyz);
        this->get_lat_lon_alt((int32_t*)lat_lon_alt);
        this->get_body_frame_origin((float*)drone_x_y_z);

        abs_pressure = DroneStateEncoder::alt_to_baro((double)lat_lon_alt[2] / 1000) * 100;
        Eigen::VectorXd mag_field_vec = magnetic_field_for_latlonalt((const int32_t*)lat_lon_alt);
        for (int i = 0; i < mag_field_vec.size(); i++) magfield[i] = mag_field_vec[i];
        // Rotate magfield according to drone orientation
        mag_field_vec = caelus_fdm::earth2body(this->get_vector_state()) * mag_field_vec;

#ifdef HIL_SENSOR_VERBOSE
        printf("[HIL_SENSOR]\n");
        printf("Body frame Acceleration (m/s**2): %f %f %f \n", body_frame_acc[0], body_frame_acc[1], body_frame_acc[2]);
        printf("Body frame xyz (NED frame) (m): %f %f %f \n", drone_x_y_z[0], drone_x_y_z[1], drone_x_y_z[2]);
        printf("GYRO xyz speed (rad/s): %f %f %f \n", gyro_xyz[0], gyro_xyz[1], gyro_xyz[2]);
        printf("Magfield (gauss): %f %f %f \n", magfield[0], magfield[1], magfield[2]);
        printf("Absolute pressure (hPa): %f\n", abs_pressure);
        printf("Differential pressure (hPa): %f\n", diff_pressure);
        printf("Alt (m) : %d \n", lat_lon_alt[2] / 1000);
        printf("Temperature (C): %f\n", this->get_temperature_reading());
        printf("Sim time %llu\n", this->get_sim_time());
#endif

        
        mavlink_msg_hil_sensor_pack(
            system_id,
            component_id,
            &msg,
            this->get_sim_time(),
            body_frame_acc[0] + randomNoise(this->noise_Acc),
            body_frame_acc[1] + randomNoise(this->noise_Acc),
            body_frame_acc[2] + randomNoise(this->noise_Acc),
            gyro_xyz[0] + randomNoise(this->noise_Gyo),
            gyro_xyz[1] + randomNoise(this->noise_Gyo),
            gyro_xyz[2] + randomNoise(this->noise_Gyo),
            magfield[0] + randomNoise(this->noise_Mag),
            magfield[1] + randomNoise(this->noise_Mag),
            magfield[2] + randomNoise(this->noise_Mag),
            abs_pressure + randomNoise(this->noise_Prs),
            diff_pressure + randomNoise(this->noise_Prs),
            lat_lon_alt[2] + randomNoise(this->noise_Prs),
            this->get_temperature_reading() + randomNoise(this->noise_Prs),
            0b1101111111111,
            0 // ID
        );

        return msg;
    }

    mavlink_message_t hil_gps_msg(uint8_t system_id, uint8_t component_id) {
        mavlink_message_t msg;
        
        // DegE7, DegE7, mm
        int32_t lon_lat_alt[3] = {0};
        // Earth-fixed NED frame (cm/s)
        uint16_t ground_speed[3] = {0};
        // Scalar horizontal speed (sqrt(vel.x**2, vel.y**2)) (see below)
        uint16_t gps_ground_speed = 0;
        // cm/s in NED earth fixed frame
        int16_t gps_velocity_ned[3] = {0};
        // Course Over Ground is the actual direction of progress of a vessel, 
        // between two points, with respect to the surface of the earth.
        uint16_t course_over_ground = 0; // 0.0..359.99 degrees // cdeg
        // number of visible satellites
        uint8_t sat_visible = 10;
        // Vehicle yaw relative to earth's north
        // Yaw of vehicle relative to Earth's North, zero means not available, use 36000 for north
        uint16_t vehicle_yaw = 0; // 0 means not available

        // Diluition of position measurements
        // Should smooth overtime from high value to low value
        // to simulate improved measurement accuracy over time.
        // TODO: Implement smoothing (Kalman filter?)
        uint16_t eph = 0.3 * 100; // minimum HDOP 
        uint16_t epv = 0.4 * 100; // minimum HDOP 

        this->get_lat_lon_alt((int32_t*)lon_lat_alt);

        this->get_earth_fixed_velocity((int16_t*)gps_velocity_ned);
        this->get_vehicle_yaw_wrt_earth_north(&vehicle_yaw);
        this->get_ground_speed((int16_t*)ground_speed);
        gps_ground_speed = sqrt(pow(ground_speed[0], 2) + pow(ground_speed[1], 2));

#ifdef HIL_GPS_VERBOSE
        printf("[GPS SENSOR]\n");
        printf("Lon Lat Alt (degE7, degE7, mm): %d %d %d \n", lon_lat_alt[0], lon_lat_alt[1], lon_lat_alt[2]);
        printf("EPH EPV (dimensionless): %d %d \n", eph, epv);
        printf("Ground speed (m/s): %d %d %d \n", ground_speed[0], ground_speed[1], ground_speed[2]);
        printf("GPS ground speed (m/s): %d\n", gps_ground_speed);
        printf("GPS velocity NED (Earth frame) (m/s): %d %d %d \n", gps_velocity_ned[0], gps_velocity_ned[1], gps_velocity_ned[2]);
        printf("Course over ground: %d \n",  course_over_ground);
        printf("Sats visible: %d \n",  sat_visible);
        printf("Vehicle yaw (deg): %d \n",  vehicle_yaw);
        printf("Sim time %llu\n", this->get_sim_time());
#endif


        mavlink_msg_hil_gps_pack(
            system_id,
            component_id,
            &msg,
            this->get_sim_time(),
            3, // 3d fix
            lon_lat_alt[0],
            lon_lat_alt[1],
            lon_lat_alt[2],
            eph,
            epv,
            gps_ground_speed,
            gps_velocity_ned[0],
            gps_velocity_ned[1],
            gps_velocity_ned[2],
            course_over_ground,
            sat_visible,
            0, // ID
            vehicle_yaw
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