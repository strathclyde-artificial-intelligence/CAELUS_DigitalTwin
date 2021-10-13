/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */
/*
------ Copyright (C) 2021 University of Strathclyde and Authors ------
-------------------- e-mail: c.greco@strath.ac.uk --------------------
----------------------- Author: Cristian Greco -----------------------
*/

#ifndef CAELUS_FDM_THRUSTFIXEDWING_H
#define CAELUS_FDM_THRUSTFIXEDWING_H
#include <cmath>
#include <utility>
#include <functional>
#include "BaseFM.h"
#include "Aerodynamics.h"

namespace caelus_fdm {

    using namespace std;

    struct prop_specs {
        int nB; // Number of blades
        double nA; // Propeller disk area
        double nR; // Propeller disc radius
        double nPh; // Absorbed power in hp (P(W) = η·√3·V·I·cosφ) η -> electric motor efficiency
        //                                                         V -> applied voltage
        //                                                         I -> absorbed current in amp
        //                                                         cosφ -> power factor
        double nb; // proportionality factor for thrust
        double nOmega; // Angular velocity propeller
    };


    class ThrustFixedWing : public BaseFM {

    protected:

        // Attributes
        function<Eigen::VectorXd(double)> m_controller = nullptr;
        double m_b; // thrust coefficient
        Eigen::VectorXd m_Omega; // Angular velocity

    public:

        ThrustFixedWing(double b, function<Eigen::VectorXd(double)> controller) :
                BaseFM(), m_b(b), m_controller(move(controller))
        {
        }

        ThrustFixedWing(double b) :
                BaseFM(), m_b(b)
        {
        }

        virtual ~ThrustFixedWing() = default;

        /**
         * Evaluate force/moment
         * @param t : time
         * @param x : state as [ x y z ...                    body-frame origin wrt earth-frame
         *                      x_dot y_dot z_dot ...         body-frame velocity
         *                      phi theta psi ...             body-frame orientation wrt earth-frame
         *                      phi_dot theta_dot psi_dot ... body-frame orientation velocity
         *                      ]
         * @param F/M: force in body-frame, not considering moments for now
         * @return
         */
        int computeF(const double &t, const State &x) override
        {
            // update parameters

            // set force
            m_F.resize(3);
            m_F[0] = m_b*pow(m_Omega(0),2.);
            m_F[1] = 0.;
            m_F[2] = 0.;
            return 0;
        }
        int computeM(const double &t, const State &x) override
        {
            // update parameters

            // set momentum
            m_M.resize(3);
            m_M[0] = 0.;
            m_M[1] = 0.;
            m_M[2] = 0.;
            return 0;
        }

        using BaseFM::getF;
        using BaseFM::getM;
        using BaseFM::updateParams;

        int updateParamsImpl(const double &t, const State &x) override {
//            this->m_controller(t, x, m_Omega);
            m_Omega = m_controller(t);
            auto state_F = this->computeF(t,x);
            auto state_M = this->computeM(t,x);
            return 0;
        }

        int setController(function<Eigen::VectorXd(double)> controller) {
            m_controller = controller;
            return 0;
        }

        double get_b_prop() {
            return m_b;
        }

        Eigen::VectorXd get_controller_prop(double t) {
            return m_controller(t);
        }

    };
}
#endif //CAELUS_FDM_THRUSTFIXEDWING_H
