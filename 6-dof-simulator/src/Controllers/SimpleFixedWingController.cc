#include "SimpleFixedWingController.h"


Eigen::VectorXd SimpleFixedWingController::none_controller(DroneConfig conf, boost::chrono::microseconds t) {
    return Eigen::VectorXd::Zero(8);
}

Eigen::VectorXd SimpleFixedWingController::hold_controller(DroneConfig conf, boost::chrono::microseconds t) {
    Eigen::VectorXd control{8};
    for (auto i = 0; i < control.size(); i++) control[i] = 0.5;
    return control;
}

Eigen::VectorXd SimpleFixedWingController::climb_controller(DroneConfig conf, boost::chrono::microseconds t) {
    Eigen::VectorXd control{8};
    for (auto i = 0; i < control.size(); i++) control[i] = 0.6;
    return control;
}

Eigen::VectorXd SimpleFixedWingController::roll_controller(DroneConfig conf, boost::chrono::microseconds t) {
    Eigen::VectorXd control{8};
    control[0] = 0.4;
    control[1] = 0.6;
    control[2] = 0.6;
    control[3] = 0.4;
    return control;
}

Eigen::VectorXd SimpleFixedWingController::pitch_controller(DroneConfig conf, boost::chrono::microseconds t) {
    Eigen::VectorXd control{8};
    control[0] = 0.6;
    control[1] = 0.4;
    control[2] = 0.6;
    control[3] = 0.4;
    return control;
}

Eigen::VectorXd SimpleFixedWingController::yaw_controller(DroneConfig conf, boost::chrono::microseconds t) {
    Eigen::VectorXd control{8};
    control[0] = 0.8;
    control[1] = 0.8;
    control[2] = 0.2;
    control[3] = 0.2;
    return control;
}

void SimpleFixedWingController::update(boost::chrono::microseconds us) {
    if (!this->executing_manoeuvre) {
        printf("[WARNING] Called QuadController update without specifying a manoeuvre plan.\n");
        return;
    }
    uint8_t sections_n = this->plan.sections_n();
    boost::chrono::microseconds current_section_length = this->plan.section_length[this->plan_cursor];

    this->manoeuvre_timer_us += us;
    this->total_timer_us += us;

    if (this->manoeuvre_timer_us >= current_section_length) {
        this->transition_to_next_manouvre();
    }
}