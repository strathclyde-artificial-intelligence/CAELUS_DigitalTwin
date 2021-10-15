/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */
/*
------ Copyright (C) 2021 University of Strathclyde and Authors ------
-------------------- e-mail: c.greco@strath.ac.uk --------------------
----------------------- Author: Cristian Greco -----------------------
*/

#ifndef CAELUS_FDM_ROTATIONMATRIX_H
#define CAELUS_FDM_ROTATIONMATRIX_H

#include "caelusFdmTypedefs.h"
#include "caelusFdmException.h"
#include "caelusFdmConstants.h"
#include <iomanip>

namespace caelus_fdm {

    /**
     * Rotation Matrix ECEF-NED,
     * @param L     Longitude (rad)
     * @param l     Latitude (rad)
     * @param h     Altitude (m)
     * @return R: Rotation Matrix
     */
    RotationMatrix ecef2ned(const double L, const double l);

    RotationMatrix ned2ecef(const double L, const double l);

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

    RotationMatrix body2wind(const State &x);

    RotationMatrix wind2body(const State &x);

    RotationMatrix body2earth(const State &x);

    RotationMatrix earth2body(const State &x);

    RotationMatrix rotateAroundAxisByAngle(double angle, unsigned int axis);


    /**
     *  Converting LlA to State in NED frame spherical earth assumption
     * @param L Long (rad)
     * @param l Lat (rad)
     * @param h Alt (m)
     * @param x State
     */
    void convertLlA2State(const double &L, const double &l, const double &h, State &x);

    /**
     * Converting State to LlA spherical earth assumption
     * @param L_in
     * @param l_in
     * @param x
     * @param Lf
     * @param lf
     * @param h
     */
    void convertState2LlA(const double L_in, const double l_in, const State &x, double &Lf, double &lf, double &h);

    /**
     * Transforming ECEF coordinates to Long, Lat and Altitude of Airy1830 Ellipsoid
     * @param xECEF
     * @param yECEF
     * @param zECEF
     * @param L
     * @param phi
     * @param H
     */
    void convertECEF2LlH(const double xECEF, const double yECEF, const double zECEF, double &L, double &phi, double &H );

    /**
     * Transforming Long, Lat, Altitude of Airy1830 Ellipsoid to ECEF coordinates
     * @param xECEF
     * @param yECEF
     * @param zECEF
     * @param L
     * @param phi
     * @param H
     */
    void convertLlH2ECEF(const double L, const double phi, const double H, double &xECEF, double &yECEF, double &zECEF );

    /**
     * Transofming Long, Lat of Airy1830 Ellipsoid to easting and northing
     * @param L
     * @param phi
     * @param E
     * @param N
     */
    void convertLl2EN(const double L, const double phi, double &E, double &N);

    /**
     * Transformation from State to Easting-Northing (British National Grid):
     * needs initial value for Long,Lat, because of flat earth assumption of the 6dof
     * @param L_in  Long initial condition (rad)
     * @param l_in  Lat initial condition (rad)
     * @param x     State
     * @param E     Easting coordinate
     * @param N     Northing coordinate
     * @param H     Altitude coordinate
     */
    void convertState2ENH(const double L_in, const double l_in, const State &x, double &E, double &N, double &H);

}

#endif //CAELUS_FDM_ROTATIONMATRIX_H