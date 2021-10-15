/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */
/*
------ Copyright (C) 2021 University of Strathclyde and Authors ------
-------------------- e-mail: c.greco@strath.ac.uk --------------------
----------------------- Author: Cristian Greco -----------------------
*/

#ifndef CAELUS_FDM_BASEFM_H
#define CAELUS_FDM_BASEFM_H

#include <cmath>
#include <utility>
#include <functional>
#include <vector>
#include "../Helpers/caelusFdmTypedefs.h"
#include "../Helpers/caelusFdmConstants.h"
#include "../Helpers/caelusFdmException.h"

namespace caelus_fdm {

    class BaseFM {

    protected:

        double m_currT = -1.e15;
        State  m_currX = {};

        Force m_F = Eigen::VectorXd::Zero(3);
        Moment m_M = Eigen::VectorXd::Zero(3);

    public:


        BaseFM() = default;

        virtual ~BaseFM() = default;

        /**
         * @param t : time
         * @param x : Input state in known reference frame
         * @param f : Output force in known reference frame
         */
        virtual int computeF(const double &t, const State &x) = 0;
        virtual int computeM(const double &t, const State &x) = 0;

    public:

        int updateParams(const double &t, const State &x) {
            if (!isCurrentTX(t,x)) {
                m_currT = t;
                m_currX = x;
                return updateParamsImpl(t, x);
            }
            return 0;
        }

        Force getF() {
            return m_F;
        }

        Moment getM() {
            return m_M;
        }

        bool isCurrentTX(double t, const State &x) {
            return (isCurrentT(t) && isCurrentX(x));
        }

        bool isCurrentT(double t) {
            return std::abs(t-m_currT)<EPS;
        }

        bool isCurrentX(const State &x) {
            if (m_currX.size()==0)
                return false;
            if (m_currX.size()!=x.size())
                caelusfdm_throw("size of x and currX do not coincide");
            for (auto i = 0; i < x.size(); i++)
                if (std::abs(x[i]-m_currX[i])>EPS)
                    return false;
            return true;
        }

    protected:

        virtual int updateParamsImpl(const double &t, const State &x)
        {
            return 0;
        }

    };

}


#endif //CAELUS_FDM_BASEFM_H
