/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */
/*
------ Copyright (C) 2021 University of Strathclyde and Authors ------
-------------------- e-mail: c.greco@strath.ac.uk --------------------
----------------------- Author: Cristian Greco -----------------------
*/

#include "angleRateRotationMatrix.h"

caelus_fdm::RotationMatrix caelus_fdm::eulerRate2angularVelocity(const State &x)
{
    auto phi = x[6], theta = x[7];
    RotationMatrix rot(3,3);
    rot << 1, 0, -sin(theta),
            0, cos(phi), sin(phi)*cos(theta),
            0, -sin(phi), cos(phi)*cos(theta);
    return rot;
}

//    RotationMatrix eulerRate2angularVelocity(const State &x)
//    {
//        auto phi = x[6], theta = x[7];
//        RotationMatrix Rpsi   = rotateAroundAxisByAngle(-psi,3);
//        RotationMatrix Rtheta = rotateAroundAxisByAngle(-theta,2);
//        RotationMatrix Rphi   = rotateAroundAxisByAngle(-phi,1);
//        RotationMatrix I =  Eigen::MatrixXd::Identity(3,3);
//        Eigen::Matrix3d rot;
//        rot.col(0) = I.col(0);
//        rot.col(1) = Rphi*I.col(1);
//        rot.col(2) = (Rphi*Rtheta)*I.col(2);
//        return rot;
//    }


caelus_fdm::RotationMatrix caelus_fdm::angularVelocity2eulerRate(const State &x)
{
    auto phi = x[6], theta = x[7];
    RotationMatrix rot(3,3);
    rot << 1, sin(phi)*tan(theta), cos(phi)*tan(theta),
            0, cos(phi), -sin(phi),
            0, sin(phi)/cos(theta), cos(phi)/cos(theta);
    return rot;
}

//    RotationMatrix angularVelocity2eulerRate(const State &x)
//    {
//        return eulerRate2angularVelocity(x).inverse().eval();
//    }