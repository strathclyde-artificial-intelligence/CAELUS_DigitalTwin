#ifndef __MATRIXXD_EXTENSION_H__
#define __MATRIXXD_EXTENSION_H__

#include "../Helpers/json.hh"
#include <Eigen/Eigen>

/**
 * Eigen::MatrixXd extension to allow population by json.
 */
struct Matrix3d : public Eigen::Matrix3d {
    Matrix3d(nlohmann::json data) {
        
        for (auto i = 0; i < 3; i++) {
            for (auto j = 0; j < 3; j++) {
                this->row(i)[j] = 0.0;
            }
        }

        this->row(0)[0] = data["jxx"];
        this->row(1)[1] = data["jyy"];
        this->row(2)[2] = data["jzz"];
        printf("Inertia matrix initialised:\n");
        std::cout << *this << std::endl;
    }
};

#endif // __MATRIXXD_EXTENSION_H__