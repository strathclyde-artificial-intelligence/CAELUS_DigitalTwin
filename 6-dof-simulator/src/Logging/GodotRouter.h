#ifndef __GODOT_ROUTER_H__
#define __GODOT_ROUTER_H__

#include "../Interfaces/DroneStateProcessor.h"
#include <Eigen/Eigen>
#include "../Helpers/rotationMatrix.h"
#include "../Helpers/rotation_utils.h"
#include "../Sockets/UDPSender.h"
#include <boost/asio.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/optional.hpp>
#include <iostream>
#include <sstream>
#include <cstdlib>
#include "../Helpers/json.hh"
#include "../Interfaces/Clock.h"

class GodotRouter : public DroneStateProcessor {
private:    
    UDPSender sender;
    Clock& clock;
public:

    GodotRouter(boost::asio::io_service& service, Clock& clock) : sender(service), clock(clock) {}

    std::stringstream state_to_json(Eigen::VectorXd state, Eigen::VectorXd dx_state) {
        nlohmann::json data;
        boost::property_tree::ptree pt;
        Eigen::VectorXd xyz = state.segment(0, 3);
        Eigen::VectorXd rpy_quat = euler_angles_to_quaternions(state.segment(6, 3));
        
        data["earth_rpy_quat"] = {rpy_quat[1], -rpy_quat[3], rpy_quat[2], rpy_quat[0]};
        data["earth_position_godot"] = {xyz[0], -xyz[2], xyz[1]};
        data["time_elapsed"] = this->clock.get_current_time_us().count() / 1000000.0;

        data["earth_position"] = {xyz[0], xyz[1], xyz[2]};
        data["body_velocity"] = {state[3], state[4], state[5]};
        data["earth_rpy"] = {state[6], state[7], state[8]};
        data["body_angular_vel"] = {state[9], state[10], state[11]};

        data["earth_velocity"] = {dx_state[0], dx_state[1], dx_state[2]};
        data["body_acceleration"] = {dx_state[3], dx_state[4], dx_state[5]};
        data["earth_rpy_dot"] = {dx_state[6], dx_state[7], dx_state[8]};
        data["body_angular_acc"] = {dx_state[9], dx_state[10], dx_state[11]};

        std::stringstream ss;
        ss << data.dump();
        return ss;
    }

    void new_drone_state(Eigen::VectorXd state, Eigen::VectorXd dx_state) {
        DroneStateProcessor::new_drone_state(state, dx_state);
        sender.send_data(state_to_json(state, dx_state).str());
    }
};

#endif // __GODOT_ROUTER_H__