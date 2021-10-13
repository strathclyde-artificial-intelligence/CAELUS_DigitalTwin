#include <boost/format.hpp>
#include <boost/thread/thread.hpp>
#include "Simulator.h"
#include "Logging/ConsoleLogger.h"

Simulator::Simulator(SimulatorConfig c) : 
    config(c),
    logger(ConsoleLogger::shared_instance())
{
    // this->message_relay.add_message_handler(this);
    this->simulation_clock.set_timestep(this->config.timestep_us);
}

Simulator::~Simulator() {}

SimulatorConfig Simulator::get_config() {
    return this->config;
}

void Simulator::add_environment_object(EnvironmentObject& e) {
    this->env_objects.push_back(&e);
}

void Simulator::update(boost::chrono::microseconds us) {
    
    if (this->simulation_clock.get_current_time_us() >= this->stop_after_us && this->stop_after_us.count() != 0) {
        printf("Simulation complete -- stopping after %lld us.\n", this->stop_after_us.count());
        this->should_shutdown = true;
        return;
    }

    this->simulation_clock.step();
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
    boost::chrono::microseconds time_increment = this->get_config().timestep_us;
    while(!this->should_shutdown) {
        if (this->config.running_lockstep) {
            boost::chrono::high_resolution_clock::time_point before;
            boost::chrono::high_resolution_clock::time_point after;
            before = boost::chrono::high_resolution_clock::now();
            this->update(time_increment);
            after = boost::chrono::high_resolution_clock::now();
            boost::chrono::microseconds computation_time = boost::chrono::duration_cast<boost::chrono::microseconds>(time_increment - (after-before));
            boost::this_thread::sleep_for((time_increment - computation_time).count() > 0 ? time_increment - computation_time : boost::chrono::microseconds{0});
        } else {
            this->update(time_increment);
            boost::this_thread::sleep_for(boost::chrono::milliseconds(4));
        }
    }

    for (auto p : this->drone_state_processors) {
        p->simulation_complete();
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