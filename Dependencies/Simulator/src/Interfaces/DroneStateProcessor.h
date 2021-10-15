#ifndef __DRONESTATEPROCESSOR_H__
#define __DRONESTATEPROCESSOR_H__

#include <Eigen/Eigen>

class DroneStateProcessor {
private:
    Eigen::VectorXd last_state{12};
    Eigen::VectorXd last_dx_state{12};
public:
    
    virtual void new_drone_state(Eigen::VectorXd state, Eigen::VectorXd dx_state) { 
        this->last_state = state;
        this->last_dx_state = dx_state;
    }
    virtual void simulation_complete() {};
    
    Eigen::VectorXd get_last_drone_state() { return last_state; }
    Eigen::VectorXd get_last_drone_dx_state() { return last_dx_state; }

};

#endif // __DRONESTATEPROCESSOR_H__