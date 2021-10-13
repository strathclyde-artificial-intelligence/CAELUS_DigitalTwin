#include "Propellers.h"
#include <math.h>

Propellers::Propellers(uint8_t propeller_n) : propeller_n(propeller_n) {
    this->_last_control = Eigen::VectorXd{propeller_n};
    this->propeller_n = propeller_n;
    for (int i = 0; i < this->propeller_n; i++) this->_last_control[i] = 0;
}

Eigen::VectorXd Propellers::control(double dt) {
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

    Eigen::VectorXd ret{this->propeller_n};
    for (uint i = 0; i < this->propeller_n; i++){
        ret[i] = ((-Mt * Me / Rs) + sqrt(pow((Mt * Me / Rs), 2) - 4 * Km * -Mt / Rs * (abs(this->_last_control[0]) * battery_voltage))) / (2 * Km);
    }
        
        

    // printf("Control for %d rotors is:\n", this->propeller_n);
    // printf("\t");
    // for (int i = 0; i < this->propeller_n; i++) printf("#%d: %f, ", i, ret[i]);
    // printf("\n-----------\n");
    // printf("\n");

    return ret;
}

void Propellers::set_control(Eigen::VectorXd c) {
    this->_last_control = c;
}
