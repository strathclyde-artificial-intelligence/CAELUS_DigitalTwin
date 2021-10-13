/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */
/*
------ Copyright (C) 2021 University of Strathclyde and Authors ------
-------------------- e-mail: c.greco@strath.ac.uk --------------------
----------------------- Author: Cristian Greco -----------------------
*/

#ifndef CAELUS_FDM_ANGLERATEROTATIONMATRIX_H
#define CAELUS_FDM_ANGLERATEROTATIONMATRIX_H

#include "rotationMatrix.h"
#include <iostream>

namespace caelus_fdm {

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

    RotationMatrix eulerRate2angularVelocity(const State &x);

    RotationMatrix angularVelocity2eulerRate(const State &x);

}

#endif //CAELUS_FDM_ANGLERATEROTATIONMATRIX_H