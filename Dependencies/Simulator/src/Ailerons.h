#ifndef __AILERON_H__
#define __AILERON_H__

#include <Eigen/Eigen>
#include "Interfaces/AsyncDroneControl.h"

#define AILERONS_N 2

class Ailerons : public AsyncDroneControl {
private:
    Eigen::VectorXd _last_control{AILERONS_N};
public:
    Ailerons();
    // [0] Left
    // [1] Right
    Eigen::VectorXd control(double dt) override;
    void set_control(Eigen::VectorXd c) override;
};


#endif // __AILERON_H__