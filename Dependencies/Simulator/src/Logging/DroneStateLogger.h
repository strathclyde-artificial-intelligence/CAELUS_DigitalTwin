#ifndef __DRONESTATELOGGER_H__
#define __DRONESTATELOGGER_H__

#include "../Interfaces/DroneStateProcessor.h"
#include <Eigen/Eigen>
#include "../Helpers/rotationMatrix.h"
#include "../Helpers/rotation_utils.h"

class DroneStateLogger : public DroneStateProcessor {

    void new_drone_state(Eigen::VectorXd state, Eigen::VectorXd dx_state) {
        DroneStateProcessor::new_drone_state(state, dx_state);
        Eigen::VectorXd gyro = state.segment(9, 3);
        Eigen::VectorXd xyz = state.segment(0, 3);
        Eigen::VectorXd rpy = euler_angles_to_quaternions(state.segment(6, 3));
        printf("^%f,%f,%f|%f,%f,%f,%f", xyz[0], xyz[1], xyz[2], rpy[0], rpy[1], rpy[2], rpy[3]);
    }
};

#endif // __DRONESTATELOGGER_H__