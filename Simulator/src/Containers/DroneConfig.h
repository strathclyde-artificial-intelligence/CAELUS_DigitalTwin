#ifndef __DRONECONFIG_H__
#define __DRONECONFIG_H__

#include <iostream>
#include <istream>
#include <fstream>
#include <Eigen/Eigen>
#include "../Interfaces/PrettyPrintable.h"
#include "../ClassExtensions/MatrixXd_Extension.h"
#include "../ClassExtensions/APM_Extension.h"

/**
 * 
 * Structure that represents all drone properties.
 * The data must be stored in a file contaning the following data (\n separated):
 * 
 * - mass
 * - thrust coefficient
 * - d
 * - c
 * - S
 * - b_aero
 * - drone_aero_config (see @ClassExtensions/APM_Extension)
 * - J (see @ClassExtensions/MatrixXd_Extension)
 * 
 */
struct DroneConfig : public PrettyPrintable {
    double mass; // kg
    double b; // thrust factor (QuadrotorEOM)
    double l; // Distance rotor from com [m]
    double b_prop; // thrust coefficient
    double d; // drag factor
    double c; // ? 
    double S; // ?
    double b_aero; // ?
    APM drone_aero_config;
    MatrixXd J; // Inertial matrix
    
    friend std::istream &operator>>(std::istream &i, DroneConfig& dc) {
        i >> dc.mass >> dc.b >> dc.l >> dc.b_prop >> dc.d >> dc.c >> dc.S >> dc.b_aero;
        // Aero Data
        i >> dc.drone_aero_config;
        // Inertial Matrix
        dc.J.resize(3,3);
        i >> dc.J;
        return i;
    }

    std::string str() override {
        return std::string(
            "<DroneConfig: m(" +
            std::to_string(this->mass) +
            ") >"
        );
    }
};

#endif // __DRONECONFIG_H__