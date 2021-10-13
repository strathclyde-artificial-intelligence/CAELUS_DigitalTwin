#ifndef __ASYNCDRONECONTROL_H__
#define __ASYNCDRONECONTROL_H__

#include <Eigen/Eigen>

class AsyncDroneControl {
public:
    ~AsyncDroneControl() {};
    virtual Eigen::VectorXd control(double dt) = 0;
    virtual void set_pwm(Eigen::VectorXd pwm) = 0;
};

#endif // __ASYNCDRONECONTROL_H__