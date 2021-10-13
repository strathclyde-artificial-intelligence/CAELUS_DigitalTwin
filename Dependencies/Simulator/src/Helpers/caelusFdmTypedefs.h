/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */
/*
------ Copyright (C) 2021 University of Strathclyde and Authors ------
-------------------- e-mail: c.greco@strath.ac.uk --------------------
----------------------- Author: Cristian Greco -----------------------
*/

#ifndef CAELUS_FDM_CAELUSFDMTYPEDEFS_H
#define CAELUS_FDM_CAELUSFDMTYPEDEFS_H

#include <vector>
#include <Eigen/Eigen>

namespace caelus_fdm {

    typedef Eigen::VectorXd State;
    typedef Eigen::VectorXd StateDerivative;
    typedef Eigen::VectorXd Angular;
    typedef Eigen::VectorXd Force;
    typedef Eigen::VectorXd Moment;
    typedef Eigen::MatrixXd RotationMatrix;

    typedef double          Sabscissa; // ascissa curvilinea
    typedef Eigen::ArrayXd  Sabscissas;

    typedef Eigen::VectorXd WayPoint;
    typedef Eigen::MatrixXd WayPoints;

}

#endif //CAELUS_FDM_CAELUSFDMTYPEDEFS_H
