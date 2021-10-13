#ifndef __PROPELLER_H__
#define __PROPELLER_H__

#include <Eigen/Eigen>
#include "Interfaces/AsyncDroneControl.h"


class Propellers : public AsyncDroneControl {
private:
    uint8_t propeller_n;
    Eigen::VectorXd _last_control;
public:
    Propellers(uint8_t propeller_n);
    // Clockwise [0:4] VTOL propeller
    // [4] Back-Thrust propeller
    Eigen::VectorXd control(double dt) override;
    void set_control(Eigen::VectorXd c) override;
};

#endif // __PROPELLER_H__