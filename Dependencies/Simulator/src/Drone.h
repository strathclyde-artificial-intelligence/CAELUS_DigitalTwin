#ifndef __DRONE_H__
#define __DRONE_H__

#include <mavlink.h>
#include <Eigen/Eigen>
#include <stdio.h>
#include <iostream>
#include <fstream>
#include <chrono>
#include <boost/numeric/odeint.hpp>
#include <boost/lockfree/queue.hpp>
#include "Containers/DroneConfig.h"
#include "Interfaces/DynamicObject.h"
#include "Interfaces/MAVLinkSystem.h"
#include "Interfaces/Alive.h"
#include "Interfaces/MAVLinkMessageRelay.h"
#include "Interfaces/MAVLinkMessageHandler.h"
#include "Interfaces/DroneStateEncoder.h"
#include "ESCs/FixedWingESC.h"
#include "DroneSensors.h"
#include "Interfaces/Clock.h"
#include "Interfaces/DroneStateProcessor.h"

class Drone : public DynamicObject,
              public MAVLinkSystem,
              public MAVLinkMessageHandler,
              public DroneStateEncoder {
protected:
    // Lockstep fix
    bool should_reply_lockstep = false;
    uint32_t hil_actuator_controls_msg_n = 0;
    uint32_t sys_time_throttle_counter = 0;

    DroneStateProcessor* drone_state_processor = NULL;
    void _publish_state(boost::chrono::microseconds dt);
    void _process_mavlink_messages();
    void fake_ground_transform(boost::chrono::microseconds us);
private:

    uint8_t mav_mode = 0;
    boost::chrono::microseconds time{0};
    boost::chrono::microseconds last_autopilot_telemetry{0};
    uint16_t hil_state_quaternion_message_frequency = 10000; // Default frequency of 10ms

    bool armed = false;

// Glasgow LatLon Height
// #define INITIAL_LAT 55.8609825
// #define INITIAL_LON -4.2488787
// #define INITIAL_ALT 2600 // mm
#define INITIAL_LAT 55.573712
#define INITIAL_LON -5.1303470010000005
#define INITIAL_ALT 2600 // mm

    DroneSensors sensors{(DynamicObject&)*this,
        LatLonAlt{ INITIAL_LAT, INITIAL_LON, INITIAL_ALT }
        };


    DroneConfig config;
    FixedWingESC virtual_esc{config};

    MAVLinkMessageRelay& connection;
    boost::lockfree::queue<mavlink_message_t, boost::lockfree::capacity<50>> message_queue;

    void _setup_drone();

    void _process_mavlink_message(mavlink_message_t m);
    void _process_command_long_message(mavlink_message_t m);
    void _process_hil_actuator_controls(mavlink_message_t m);

    void _publish_hil_gps();
    void _publish_hil_state_quaternion();
    void _publish_hil_sensor();
    void _publish_system_time();

public:

    Drone(const char* config_file, MAVLinkMessageRelay& connection, Clock& clock);
    ~Drone() {};

    DroneConfig get_config() { return this->config; }
    bool is_armed() { return this->armed; }

    void update(boost::chrono::microseconds us) override;
    MAVLinkMessageRelay& get_mavlink_message_relay() override;
    // Receives mavlink message from non-main thread
    // Should store messages in queue and process them within the update loop.
    void handle_mavlink_message(mavlink_message_t m) override;

    void set_drone_state_processor(DroneStateProcessor& processor) {
        this->drone_state_processor = &processor;
    }

    uint64_t get_sim_time() override;
    uint8_t get_mav_mode() override;
    Sensors& get_sensors() override;
    
    Eigen::VectorXd get_state() {
        return this->state;
    }
    Eigen::VectorXd get_dx_state() {
        return this->dx_state;
    };
};

#endif // __DRONE_H__