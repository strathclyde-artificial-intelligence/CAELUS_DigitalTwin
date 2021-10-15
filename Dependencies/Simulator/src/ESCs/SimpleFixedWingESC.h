#ifndef __SIMPLE_FIXEDWINGESC_H__
#define __SIMPLE_FIXEDWINGESC_H__

#include "../Interfaces/AsyncDroneControl.h"
#include "../Containers/DroneConfig.h"

class SimpleFixedWingESC : public AsyncDroneControl {
private:
    DroneConfig config;
    uint8_t pwm_control_size = 8;
    Eigen::VectorXd last_control{pwm_control_size};
protected:
    Eigen::VectorXd control_for_vtol_propellers(Eigen::VectorXd vtol_pwm) {
        Eigen::VectorXd ret{4};
        // (2.0*...) => With 0.5 pwm control we must get a hover
        // This is to make sure that the SimpleFixedWingController is able to manoeuver without being a
        // full blown PID controller (it has no feedback)
        double omega = 2.0*sqrt(this->config.mass*9.81/this->config.vtol_komega/4.);

        ret[0] = omega * vtol_pwm[0];
        ret[1] = omega * vtol_pwm[3];
        ret[2] = omega * vtol_pwm[1];
        ret[3] = omega * vtol_pwm[2];

        return ret;
    }

    Eigen::VectorXd control_for_thrust_propeller(Eigen::VectorXd thrust_pwm) {
        return Eigen::VectorXd::Zero(2);
    }

    Eigen::VectorXd control_for_elevons(Eigen::VectorXd elevons_pwm) {
        return Eigen::VectorXd::Zero(2);
    }

public:
    SimpleFixedWingESC(DroneConfig config) : config(config) {};

    Eigen::VectorXd control(double dt) override {
        Eigen::VectorXd controls{this->pwm_control_size};
        Eigen::VectorXd vtol_control = this->control_for_vtol_propellers(this->last_control.segment(0, 4));
        Eigen::VectorXd thrust_control = this->control_for_thrust_propeller(this->last_control.segment(4, 2));
        Eigen::VectorXd elevons_control = this->control_for_elevons(this->last_control.segment(6, 2));
        controls.segment(0, 4) = vtol_control;
        controls.segment(4, 2) = thrust_control;
        controls.segment(6, 2) = elevons_control;
        return controls;
    }

    void set_pwm(Eigen::VectorXd c) override {
        this->last_control = c;
    }
};

#endif // __SIMPLE_FIXEDWINGESC_H__