#ifndef __QUADROTOR_ESC_H__
#define __QUADROTOR_ESC_H__
#include <tgmath.h> 
#include "../Interfaces/AsyncDroneControl.h"
#include "../Containers/DroneConfig.h"

class QuadrotorESC : public AsyncDroneControl {
private:
    DroneConfig config;
    uint8_t pwm_control_size = 8;
    Eigen::VectorXd last_pwm = Eigen::VectorXd::Zero(pwm_control_size);
    Eigen::VectorXd last_control = Eigen::VectorXd::Zero(4);
protected:
    Eigen::VectorXd control_for_vtol_propellers(Eigen::VectorXd vtol_pwm) {
        Eigen::VectorXd ret{4};
        double dt = 0.004;
        std::vector<int> control_remap = {0, 3, 1, 2};

        for (auto i = 0; i < 4; i++) {
            auto new_pwm = (this->last_control[i] + (vtol_pwm[control_remap[i]] - this->last_control[i]) * (1.0 - exp(-dt / this->config.vtol_tau)));
            this->last_control[i] = new_pwm;
            ret[i] = new_pwm * this->config.vtol_kv;
        }

        return ret;
    }

    Eigen::VectorXd control_for_thrust_propeller(Eigen::VectorXd thrust_pwm) {
        return Eigen::VectorXd::Zero(2);
    }

    Eigen::VectorXd control_for_elevons(Eigen::VectorXd elevons_pwm) {
        return Eigen::VectorXd::Zero(2);
    }

public:
    QuadrotorESC(DroneConfig config) : config(config) {};

    Eigen::VectorXd control(double dt) override {
        Eigen::VectorXd controls{this->pwm_control_size};
        Eigen::VectorXd vtol_control = this->control_for_vtol_propellers(this->last_pwm.segment(0, 4));
        Eigen::VectorXd thrust_control = this->control_for_thrust_propeller(this->last_pwm.segment(4, 2));
        Eigen::VectorXd elevons_control = this->control_for_elevons(this->last_pwm.segment(6, 2));
        controls.segment(0, 4) = vtol_control;
        controls.segment(4, 2) = thrust_control;
        controls.segment(6, 2) = elevons_control;
        return controls;
    }

    void set_pwm(Eigen::VectorXd c) override {
        this->last_pwm = c;
    }
};

#endif // __QUADROTOR_ESC_H__