#ifndef __MAVLINKSYSTEM_H__
#define __MAVLINKSYSTEM_H__

#pragma GCC diagnostic ignored "-Wdeprecated-declarations"

#include <mavlink.h>
#include <chrono>
#include <boost/asio.hpp>
#include "TimeHandler.h"
#include "MAVLinkMessageRelay.h"
#include "Alive.h"

using namespace boost::asio;


class MAVLinkSystem : public Alive, public TimeHandler {
private:
    // Microseconds
    double heartbeat_interval = 500 * 1000; // 500ms to us
    std::chrono::steady_clock::time_point last_heartbeat = std::chrono::steady_clock::now();
public:
    uint8_t system_id;
    uint8_t component_id;

    virtual MAVLinkMessageRelay& get_mavlink_message_relay() = 0;
    virtual uint8_t get_mav_mode() = 0;

    MAVLinkSystem(uint8_t system_id, uint8_t component_id) : 
        system_id(system_id), 
        component_id(component_id) {}
    
    virtual double get_heartbeat_interval() override { return this->heartbeat_interval; }
    virtual void set_heartbeat_interval(double interval) override { this->heartbeat_interval = interval; }

    void update(boost::chrono::microseconds us) override {
        auto now = std::chrono::steady_clock::now();
        double elapsed_time = std::chrono::duration_cast<std::chrono::microseconds>(now - this->last_heartbeat).count();
        if (elapsed_time >= this->heartbeat_interval) {
            this->send_heartbeat();
            this->last_heartbeat = now;
        }
    }

    void send_heartbeat() override {
        MAVLinkMessageRelay& relay = this->get_mavlink_message_relay();
        if (!relay.connection_open()) { return; }
        mavlink_message_t hb;
        mavlink_msg_heartbeat_pack(this->system_id, this->component_id, &hb, MAV_TYPE_VTOL_QUADROTOR, MAV_AUTOPILOT_PX4, this->get_mav_mode(), 0, MAV_STATE_STANDBY);
        relay.send_message(hb);
    }

    void received_heartbeat() override {
        printf("Hearbeat received from PX4\n");
    }
    
};

#endif // __MAVLINKSYSTEM_H__