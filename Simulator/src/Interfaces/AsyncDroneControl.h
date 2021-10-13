#ifndef __ASYNCDRONECONTROL_H__
#define __ASYNCDRONECONTROL_H__

#include <Eigen/Eigen>

class AsyncDroneControl {
public:
    ~AsyncDroneControl() {};
    virtual Eigen::VectorXd control(double dt) = 0;
    virtual void set_control(Eigen::VectorXd c) = 0;
};

#endif // __ASYNCDRONECONTROL_H__