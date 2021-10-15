#ifndef __DRONECONFIG_H__
#define __DRONECONFIG_H__

#include <iostream>
#include <istream>
#include <fstream>
#include <Eigen/Eigen>
#include "../Interfaces/PrettyPrintable.h"
#include "../ClassExtensions/Matrix3d_Extension.h"
#include "../ClassExtensions/APM_Extension.h"
#include "../Helpers/json.hh"

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
    double mass = 0; // kg

    double vtol_komega = 0;
    double vtol_kv = 0;
    double vtol_klift = 0;
    double vtol_tau = 0;
    double vtol_lcog = 0;
    double vtol_tdrag = 0;

    double thruster_komega = 0;
    double thruster_kv = 0;
    double thruster_klift = 0;
    double thruster_tau = 0;
    double thruster_lcog = 0;
    double thruster_tdrag = 0;

    double c = 0; // ? 
    double S = 0; // ?
    double b_aero = 0; // ?
    APM drone_aero_config;
    Matrix3d J; // Inertial matrix

    DroneConfig(nlohmann::json data) : J(data) {
        mass = data["mass"];
        vtol_komega = data["vtol_komega"];
        vtol_kv = data["vtol_kv"];
        vtol_klift = data["vtol_klift"];
        vtol_tau = data["vtol_tau"];
        vtol_lcog = data["vtol_lcog"];
        vtol_tdrag = data["vtol_tdrag"];
        thruster_komega = data["thruster_komega"];
        thruster_kv = data["thruster_kv"];
        thruster_klift = data["thruster_klift"];
        thruster_tau = data["thruster_tau"];
        thruster_lcog = data["thruster_lcog"];
        thruster_tdrag = data["thruster_tdrag"];
    }

    std::string str() override {
        return std::string(
            "<DroneConfig: m(" +
            std::to_string(this->mass) +
            ") >"
        );
    }
};

static DroneConfig config_from_file_path(const char* path) {
    std::ifstream fin(path);
    nlohmann::json data = nlohmann::json::parse(fin);
    DroneConfig conf{data};
    return conf;
}

#endif // __DRONECONFIG_H__