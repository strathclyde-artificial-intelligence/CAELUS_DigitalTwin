/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */
/*
------ Copyright (C) 2021 University of Strathclyde and Authors ------
-------------------- e-mail: c.greco@strath.ac.uk --------------------
----------------------- Author: Cristian Greco -----------------------
*/

#ifndef CAELUS_FDM_DRAG_H
#define CAELUS_FDM_DRAG_H

#include "../Helpers/rotationMatrix.h"
#include "BaseFM.h"
#include "../Containers/DroneConfig.h"

namespace caelus_fdm {

    class Drag : public BaseFM {

    protected:

        // Attributes
        double rho = 1.225;  // air density
        double drag_coefficient = 0.157;     // drag coeff

    public:

        explicit Drag(DroneConfig config) :
            BaseFM(), rho(1.225), drag_coefficient(0.157)
        {
            printf("Drag model initialised with params:\n");
            printf("\t rho: %f\n", rho);
            printf("\t drag_coefficient: %f\n", drag_coefficient);
        }

        virtual ~Drag() = default;

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
            Eigen::Vector3d Vb = x.segment(3,3);
            double k = -1/2 * rho * drag_coefficient;
            m_F = k * Vb.norm() * Vb;
            return 0;
        }
        int computeM(const double &t, const State &x) override {
            m_M.resize(3);
            m_M[0] = 0.;
            m_M[1] = 0.;
            m_M[2] = 0.;
            return 0;
        }

        int updateParamsImpl(const double &t, const State &x) override {
            auto state_F = this->computeF(t,x);
            auto state_M = this->computeM(t,x);
            return 0;
        }

    };
}


#endif //CAELUS_FDM_DRAG_H
