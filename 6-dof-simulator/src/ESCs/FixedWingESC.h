#ifndef __FIXEDWINGESC_H__
#define __FIXEDWINGESC_H__

#include "../Interfaces/AsyncDroneControl.h"
#include "../Containers/DroneConfig.h"

class FixedWingESC : public AsyncDroneControl {
private:
    DroneConfig config;
    uint8_t pwm_control_size = 8;
    Eigen::VectorXd last_pwm = Eigen::VectorXd::Zero(pwm_control_size);
    Eigen::VectorXd last_control = Eigen::VectorXd::Zero(4);
protected:
    Eigen::VectorXd control_for_vtol_propellers(Eigen::VectorXd vtol_pwm) {
        // Using Erik's formula for omega here
        // Motor parameters -- temporary! Move to somewhere more proper.
        double Kt = 6.2e-05; // thrust [N] 
        double Km = Kt / 42.0; // torque [Nm]
        double Me = 1.0 / (490 * 3.14159265 / 30); // back EMF constant [V / [rad/s]]
        double Mt = Me; // torque constant [Nm/Amp]

        double Ly = 0.4; 
        double Lx = 1.09;
        double Lxf = 0.456;
        double Lxr = Lx - Lxf;

        double Scell = 7.0;
        double Rs = 0.10;
        double lm = 0.0007;
        
        double lxx = 1.0;
        double lxy = 0.05;
        double lxz = 0.05;
        double lyx = 0.05;
        double lyy = 1.5;
        double lyz = 0.05;
        double lzx = 0.05;
        double lzy = 0.05;
        double lzz = 2.0;

        double Mcg = 14.5;
        double battery_voltage = 4.0;

        Eigen::VectorXd ret{4};

        double omega_coeff = (this->config.vtol_kv / (1 + this->config.vtol_tau * 0.004));

        // Iris quad
        double dt = 0.004;
        std::vector<int> control_remap = {0, 3, 1, 2};

        for (auto i = 0; i < 4; i++) {
            ret[i] = this->last_control[i] + ((dt * (this->config.vtol_kv * vtol_pwm[control_remap[i]] - this->last_control[i])) / this->config.vtol_tau);
            this->last_control[i] = ret[i];
        }

        // + quad
        // ret[0] = 1.5 * omega * vtol_pwm[2];
        // ret[1] = 1.5 * omega * vtol_pwm[0];
        // ret[2] = 1.5 * omega * vtol_pwm[3];
        // ret[3] = 1.5 * omega * vtol_pwm[1];
        

        // for (uint i = 0; i < 4; i++){
        //     ret[i] = 1.2 * omega * vtol_pwm[i]; //2*((-Mt * Me / Rs) + sqrt(pow((Mt * Me / Rs), 2) - 4 * Km * -Mt / Rs * (abs(vtol_pwm[i]) * battery_voltage))) / (2 * Km);
        // }
        return ret;
    }

    Eigen::VectorXd control_for_thrust_propeller(Eigen::VectorXd thrust_pwm) {
        return Eigen::VectorXd::Zero(2);
    }

    Eigen::VectorXd control_for_elevons(Eigen::VectorXd elevons_pwm) {
        return Eigen::VectorXd::Zero(2);
    }

public:
    FixedWingESC(DroneConfig config) : config(config) {};

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

#endif // __FIXEDWINGESC_H__