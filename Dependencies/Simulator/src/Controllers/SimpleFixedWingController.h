#ifndef __SIMPLE_FIXED_WING_CONTROLLER__
#define __SIMPLE_FIXED_WING_CONTROLLER__

#include "../Interfaces/DroneController.h"
#include "../Containers/DroneConfig.h"
#include "../Interfaces/TimeHandler.h"
#include <Eigen/Eigen>
#include <boost/chrono.hpp>
#include <stdio.h>

enum Manoeuvre { NONE, CLIMB, HOLD, ROLL, PITCH, YAW };

struct ManoeuvrePlan {
    std::vector<boost::chrono::microseconds> section_length;
    std::vector<Manoeuvre> manoeuvre;
    size_t sections_n() {
        return this->section_length.size();
    };
};

static const char* manouvre_name(Manoeuvre m) {
    switch(m) {
        case Manoeuvre::NONE:
            return "Shut down";
        case Manoeuvre::CLIMB:
            return "Climb";
        case Manoeuvre::HOLD:
            return "Hold";
        case Manoeuvre::ROLL:
            return "Roll";
        case Manoeuvre::PITCH:
            return "Pitch";
        case Manoeuvre::YAW:
            return "Yaw";
        default:
            return "Unknown Manouvre";
    }
}

class SimpleFixedWingController : public DroneController {
protected: 
    DroneConfig config;

    ManoeuvrePlan plan;
    bool executing_manoeuvre = false;
    uint8_t plan_cursor = 0;

    boost::chrono::microseconds manoeuvre_timer_us{0};
    boost::chrono::microseconds total_timer_us{0};

    static Eigen::VectorXd none_controller(DroneConfig conf, boost::chrono::microseconds t);
    static Eigen::VectorXd hold_controller(DroneConfig conf, boost::chrono::microseconds t);
    static Eigen::VectorXd climb_controller(DroneConfig conf, boost::chrono::microseconds t);
    static Eigen::VectorXd roll_controller(DroneConfig conf, boost::chrono::microseconds t);
    static Eigen::VectorXd pitch_controller(DroneConfig conf, boost::chrono::microseconds t);
    static Eigen::VectorXd yaw_controller(DroneConfig conf, boost::chrono::microseconds t);

    void transition_to_next_manouvre() {

        if (this->plan_cursor + 2 > this->plan.sections_n()) {
            fprintf(stdout, "[END] Manouvre plan complete (now: %lld us).\n", this->total_timer_us.count());
            this->manoeuvre_timer_us = boost::chrono::microseconds{0};
            this->total_timer_us = boost::chrono::microseconds{0};
            this->executing_manoeuvre = false;
            return;
        } this->plan_cursor++;

        Manoeuvre next_manouvre = this->plan.manoeuvre[this->plan_cursor];
        boost::chrono::microseconds section_length = this->plan.section_length[this->plan_cursor];
        fprintf(stdout, "[TRANSITION] Starting %s (now: %lld us) (manoeuvre duration: %lld us)\n", manouvre_name(next_manouvre), this->total_timer_us.count(), section_length.count());
        this->manoeuvre_timer_us = boost::chrono::microseconds{0};
    }

public:
    SimpleFixedWingController(DroneConfig config) : config(config) {};

    Manoeuvre get_current_manoeuvre() { return this->plan.manoeuvre[this->plan_cursor]; }
    boost::chrono::microseconds get_current_manoeuvre_duration() { return this->plan.section_length[this->plan_cursor]; }
    
    boost::chrono::microseconds get_total_plan_duration_us() {
        boost::chrono::microseconds duration{0};
        uint8_t manoeuvres_n = this->plan.sections_n();
        for (auto i = 0; i < manoeuvres_n; i++) duration += this->plan.section_length[i];
        return duration;
    }

    auto controller_for_manoeuvre() -> Eigen::VectorXd(*)(DroneConfig, boost::chrono::microseconds) {
        switch(this->get_current_manoeuvre()) {
            case Manoeuvre::NONE:
                return &SimpleFixedWingController::none_controller;
            case Manoeuvre::CLIMB:
                return &SimpleFixedWingController::climb_controller;
            case Manoeuvre::HOLD:
                return &SimpleFixedWingController::hold_controller;
            case Manoeuvre::ROLL:
                return &SimpleFixedWingController::roll_controller;
            case Manoeuvre::PITCH:
                return &SimpleFixedWingController::pitch_controller;
            case Manoeuvre::YAW:
                return &SimpleFixedWingController::yaw_controller;
            default:
                fprintf(stdout, "Unknown manoeuvre! (%d)\n", this->get_current_manoeuvre());
                std::exit(-1);
        }
    }

    void set_plan(ManoeuvrePlan plan) {
        uint8_t manoeuvres_n = plan.sections_n();
        this->manoeuvre_timer_us = boost::chrono::microseconds{0};
        this->total_timer_us = boost::chrono::microseconds{0};
        this->executing_manoeuvre = true;
        this->plan = plan;
        this->plan_cursor = 0;
        boost::chrono::microseconds duration = this->get_current_manoeuvre_duration();
        fprintf(stdout, "[NEW PLAN] Manoeuvres n: %d | total duration (us): %lld\n", manoeuvres_n, duration.count());
        fprintf(stdout, "[INITIAL_MANOEUVRE] Starting -> %s (%lld us)\n", manouvre_name(this->get_current_manoeuvre()), this->get_current_manoeuvre_duration().count());
    }

    Eigen::VectorXd get_current_pwm_control() {
        auto func = this->controller_for_manoeuvre();
        return func(this->config, this->manoeuvre_timer_us);
    }
    
    virtual Eigen::VectorXd control(double dt) override {
        return this->get_current_pwm_control();
    }

    virtual void set_pwm(Eigen::VectorXd c) override {};
    void update(boost::chrono::microseconds us) override;
};

#endif // __SIMPLE_FIXED_WING_CONTROLLER__