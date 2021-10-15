/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */
/*
------ Copyright (C) 2021 University of Strathclyde and Authors ------
-------------------- e-mail: c.greco@strath.ac.uk --------------------
----------------------- Author: Cristian Greco -----------------------
*/

#ifndef CAELUS_FDM_THRUSTQUADROTOR_H
#define CAELUS_FDM_THRUSTQUADROTOR_H

#include "BaseFM.h"
#include "../Helpers/json.hh"

namespace caelus_fdm {

    using namespace std;

    class ThrustQuadrotor : public BaseFM {

    protected:

        // Attributes
        function<Eigen::VectorXd(double)> m_controller = NULL;
        double vtol_komega = 0;
        double vtol_kv = 0;
        double vtol_klift = 0;
        double vtol_tdrag = 0;
        double vtol_tau = 0;
        double vtol_lcog = 0;

        Eigen::VectorXd m_Omega;

    public:

        ThrustQuadrotor(DroneConfig config) :
                BaseFM(),
                vtol_komega(config.vtol_komega),
                vtol_kv(config.vtol_kv),
                vtol_klift(config.vtol_klift),
                vtol_tdrag(config.vtol_tdrag),
                vtol_tau(config.vtol_tau),
                vtol_lcog(config.vtol_lcog)
        {
            printf("Quadrotor thrust model initialised with params:\n");
            printf("\t vtol_komega: %f\n", this->vtol_komega);
            printf("\t vtol_kv: %f\n", this->vtol_kv);
            printf("\t vtol_klift: %f\n", this->vtol_klift);
            printf("\t vtol_tdrag: %f\n", this->vtol_tdrag);
            printf("\t vtol_tau: %f\n", this->vtol_tau);
            printf("\t vtol_lcog: %f\n", this->vtol_lcog);
        }

        virtual ~ThrustQuadrotor() = default;

        /**
         * Rotation Matrix Wind to Body Frame [Gryte, “Aerodynamic  modeling  of  the  Skywalker  X8  Fixed-Wing  UnmannedAerial  Vehicle”]
         * @param x : state as [ x y z ...                    body-frame origin wrt earth-frame
         *                      x_dot y_dot z_dot ...         body-frame velocity
         *                      phi (roll) theta (pitch) psi (yaw) ...             body-frame orientation wrt earth-frame
         *                      phi_dot theta_dot psi_dot ... body-frame orientation velocity
         *                      ]
         * @param R: Rotation Matrix Wind to Body frame
         * @return
         */

        int computeF(const double &t, const State &x) override
        {
            // this https://core.ac.uk/download/pdf/48657308.pdf
            m_F.resize(3);
            m_F[0] = 0.;
            m_F[1] = 0.;
            m_F[2] = -this->vtol_komega*(pow(m_Omega[0],2.)+pow(m_Omega[1],2.)+pow(m_Omega[2],2.)+pow(m_Omega[3],2.));
            return 0;
        }
        int computeM(const double &t, const State &x) override
        {
            double r0_f = this->vtol_komega * pow(m_Omega[0], 2);
            double r1_f = this->vtol_komega * pow(m_Omega[1], 2);
            double r2_f = this->vtol_komega * pow(m_Omega[2], 2);
            double r3_f = this->vtol_komega * pow(m_Omega[3], 2);

            m_M.resize(3);
            // this https://core.ac.uk/download/pdf/48657308.pdf
            m_M[0] = (sqrt(2) / 2) * this->vtol_lcog * ((r3_f+r2_f) - (r0_f+r1_f));
            m_M[1] = (sqrt(2) / 2) * this->vtol_lcog * ((r3_f+r0_f) - (r1_f+r2_f));
            m_M[2] = this->vtol_tdrag * (m_Omega[0]-m_Omega[1]+m_Omega[2]-m_Omega[3]);
            return 0;
        }

        int updateParamsImpl(const double &t, const State &x) override {
            m_Omega = m_controller(t);
            auto state_F = computeF(t,x);
            auto state_M = computeM(t,x);
            return 0;
        } 

        int setController(function<Eigen::VectorXd(double)> controller) {
            this->m_controller = controller;
            return 0;
        }
    };

}



#endif //CAELUS_FDM_THRUSTQUADROTOR_H
