#ifndef __ROTATION_UTILS_H__
#define __ROTATION_UTILS_H__

#include <Eigen/Eigen>
#include <cmath>

inline Eigen::VectorXd euler_angles_to_quaternions(const Eigen::Vector3d euler_rpy) {
        Eigen::VectorXd quaternion{4};

        float roll = euler_rpy[0];
        float pitch = euler_rpy[1];
        float yaw = euler_rpy[2];
        
        double cy = cos(yaw * 0.5);
        double sy = sin(yaw * 0.5);
        double cp = cos(pitch * 0.5);
        double sp = sin(pitch * 0.5);
        double cr = cos(roll * 0.5);
        double sr = sin(roll * 0.5);
        
        // Order should be w x y z 
        quaternion[0] = cr * cp * cy + sr * sp * sy;
        quaternion[1] = sr * cp * cy - cr * sp * sy;
        quaternion[2] = cr * sp * cy + sr * cp * sy;
        quaternion[3] = cr * cp * sy - sr * sp * cy;
        
        return quaternion;
}
    
#endif // __ROTATION_UTILS_H__