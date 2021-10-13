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
#include "ClassExtensions/MixedEOM_Extension.h"
#include "Interfaces/MAVLinkMessageRelay.h"
#include "Interfaces/MAVLinkMessageHandler.h"
#include "Interfaces/DroneStateEncoder.h"
#include "Propellers.h"
#include "Ailerons.h"

#define STATE_SIZE 12

typedef boost::numeric::odeint::runge_kutta_dopri5<Eigen::VectorXd,double,Eigen::VectorXd,double,boost::numeric::odeint::vector_space_algebra> ODESolver;

class Drone : public DynamicObject,
              public MAVLinkSystem,
              public MAVLinkMessageHandler,
              public DroneStateEncoder {
private:

    // Lockstep fix
    bool should_reply_lockstep = false;
    uint32_t hil_actuator_controls_msg_n = 0;
    uint32_t sys_time_throttle_counter = 0;
    
    uint8_t mav_mode = 0;
    boost::chrono::microseconds time{0};
    boost::chrono::microseconds last_autopilot_telemetry{0};
    uint16_t hil_state_quaternion_message_frequency = 1000000; // Default frequency of 1s

    bool armed = false;

    Propellers thrust_propellers{1};
    Propellers vtol_propellers{4};
    Ailerons ailerons;

    DroneConfig config;

    Eigen::VectorXd state;
    Eigen::VectorXd dx_state;
    MixedEOM dynamics;
    ODESolver dynamics_solver;

    MAVLinkMessageRelay& connection;
    boost::lockfree::queue<mavlink_message_t, boost::lockfree::capacity<50>> message_queue;

    void _setup_drone();

    void _process_mavlink_message(mavlink_message_t m);
    void _process_mavlink_messages();
    void _process_command_long_message(mavlink_message_t m);
    void _process_hil_actuator_controls(mavlink_message_t m);

    void _publish_hil_gps();
    void _publish_hil_state_quaternion();
    void _publish_hil_sensor();
    void _publish_state(boost::chrono::microseconds dt);
    void _publish_system_time();
    
    void _step_dynamics(boost::chrono::microseconds us);
public:

    Drone(char* config_file, MAVLinkMessageRelay& connection);
    ~Drone() {};

    Eigen::VectorXd& get_state() override { return this->state; }
    DroneConfig get_config() { return this->config; }
    bool is_armed() { return this->armed; }

    void update(boost::chrono::microseconds us) override;
    MAVLinkMessageRelay& get_mavlink_message_relay() override;
    // Receives mavlink message from non-main thread
    // Should store messages in queue and process them within the update loop.
    void handle_mavlink_message(mavlink_message_t m) override;

    uint64_t get_sim_time() override;
    Eigen::Vector3d get_environment_wind() override;
    float get_temperature_reading() override;
    uint8_t get_mav_mode() override;

    Eigen::VectorXd& get_vector_state() override;
    Eigen::VectorXd& get_vector_dx_state() override;
};

#endif // __DRONE_H__