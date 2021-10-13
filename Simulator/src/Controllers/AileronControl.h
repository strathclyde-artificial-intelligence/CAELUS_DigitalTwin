#ifndef __AILERONCONTROL_H__
#define __AILERONCONTROL_H__

#include "Interfaces/AsyncDroneControl.h"

class AileronControl : public AsyncDroneControl {
private:
    Eigen::VectorXd last_control;
public:
    Eigen::VectorXd get_control(double dt) override;
    Eigen::VectorXd last_control() override;
    void set_control(Eigen::VectorXd c) override;
}

#endif // __AILERONCONTROL_H__