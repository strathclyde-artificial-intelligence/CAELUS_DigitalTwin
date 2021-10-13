#include <boost/format.hpp>
#include <boost/thread/thread.hpp>
#include "Simulator.h"
#include "Logging/ConsoleLogger.h"

Simulator::Simulator(SimulatorConfig c, MAVLinkMessageRelay& message_relay) : 
    config(c),
    message_relay(message_relay),
    logger(ConsoleLogger::shared_instance())
{
    // this->message_relay.add_message_handler(this);
} 

Simulator::~Simulator() {}

SimulatorConfig Simulator::get_config() {
    return this->config;
}

void Simulator::add_environment_object(EnvironmentObject& e) {
    this->env_objects.push_back(&e);
}

void Simulator::update(boost::chrono::microseconds us) {
    this->_process_mavlink_messages();
    for (auto e : this->env_objects) {
        e->update(us);
    }
}

void Simulator::handle_mavlink_message(mavlink_message_t m) {
    this->message_queue.push(m);
}

void Simulator::start() {
    this->logger->log(SIMULATION_STARTED);
    boost::chrono::steady_clock c;
    boost::chrono::time_point t = c.now();
    while(!this->should_shutdown) {
        if (this->config.running_lockstep) {
            // boost::chrono::time_point now = c.now();
            // boost::chrono::microseconds elapsed_time = boost::chrono::duration_cast<boost::chrono::microseconds>(now - t);
            boost::chrono::microseconds time_increment = this->should_advance_time ? this->get_config().timestep_us : boost::chrono::microseconds(0);
            this->update(time_increment);
            this->simulation_time += time_increment;    
            this->should_advance_time = true;
            boost::this_thread::sleep_for(boost::chrono::microseconds(3000));
            // t = now;
        } else {
            printf("RUNNING IN NON-LOCKSTEP!\n");
            this->update(this->config.timestep_us);
            this->simulation_time += this->config.timestep_us;
            // boost::this_thread::sleep_for(boost::chrono::microseconds(this->config.timestep_us));
        }
    }
}

void Simulator::_process_mavlink_message(mavlink_message_t m) {
    this->should_advance_time = true;
}

void Simulator::_process_mavlink_messages() {
    this->message_queue.consume_all([this](mavlink_message_t m){
        this->_process_mavlink_message(m);
    });
}

void Simulator::pause() {
    this->logger->log(SIMULATION_PAUSED);
}

void Simulator::resume() {
    this->logger->log(SIMULATION_RESUMED);
}

std::string Simulator::str() {
    SimulatorConfig c = this->get_config();
    return std::string(
        "<Simulator timestep: " + 
        std::to_string(c.timestep_us.count()) + 
        " | speed_mult: " +
        std::to_string(c.max_speed_multiplier) +
        " >"
    );
}
