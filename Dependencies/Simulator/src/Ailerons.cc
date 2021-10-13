#include "Ailerons.h"

Ailerons::Ailerons() {
    for (int i = 0; i < AILERONS_N; i++) this->_last_control[i] = 0;
}

Eigen::VectorXd Ailerons::control(double dt) {
    return this->_last_control;
}

void Ailerons::set_control(Eigen::VectorXd c) {
    this->_last_control = c;
}
