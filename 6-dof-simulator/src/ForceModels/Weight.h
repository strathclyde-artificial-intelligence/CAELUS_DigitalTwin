/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */
/*
------ Copyright (C) 2021 University of Strathclyde and Authors ------
-------------------- e-mail: c.greco@strath.ac.uk --------------------
----------------------- Author: Cristian Greco -----------------------
*/

#ifndef CAELUS_FDM_WEIGHT_H
#define CAELUS_FDM_WEIGHT_H

#include "../Helpers/rotationMatrix.h"
#include "BaseFM.h"
#include "../Containers/DroneConfig.h"

namespace caelus_fdm {

    class Weight : public BaseFM {

    protected:

        // Attributes
        double mass;  // quadrotor mass
        double m_g;     // grav force per unit of mass

    public:

        explicit Weight(DroneConfig config ,double g = 9.81) :
            BaseFM(), mass(config.mass), m_g(g)
        {
            printf("Weight model initialised with params:\n");
            printf("\t mass: %f\n", mass);
            printf("\t gravity acc: %f\n", m_g);
        }

        virtual ~Weight() = default;

        /**
         * Evaluate force/moment
         * @param t : time
         * @param x : state as [ x y z ...                     body-frame origin wrt earth-frame
         *                       u v w  ...                    body-frame velocity
         *                       phi theta psi ...             body-frame orientation wrt earth-frame
         *                       phi_dot theta_dot psi_dot ... body-frame orientation velocity
         *                      ]
         * @param F/M: force/moment in body-frame
         * @return
         */
        int computeF(const double &t, const State &x) override {
            m_F.resize(3);
            m_F[0] = 0.;
            m_F[1] = 0.;
            m_F[2] = m_g*mass; // TODO GAETANO CHANGE IF NECESSARY //
            m_F    = earth2body(x)*m_F;
            return 0;
        }
        int computeM(const double &t, const State &x) override {
            m_M.resize(3);
            m_M[0] = 0.;
            m_M[1] = 0.;
            m_M[2] = 0.;
            return 0;
        }

        double get_mass() const {
            return mass;
        }

        int updateParamsImpl(const double &t, const State &x) override {
            auto state_F = this->computeF(t,x);
            auto state_M = this->computeM(t,x);
            return 0;
        }

    };
}


#endif //CAELUS_FDM_WEIGHT_H
