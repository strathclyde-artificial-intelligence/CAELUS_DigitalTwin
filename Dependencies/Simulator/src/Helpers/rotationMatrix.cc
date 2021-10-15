/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */
/*
------ Copyright (C) 2021 University of Strathclyde and Authors ------
-------------------- e-mail: c.greco@strath.ac.uk --------------------
----------------------- Author: Cristian Greco -----------------------
*/
#include "rotationMatrix.h"

using namespace std;
using namespace caelus_fdm;

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
RotationMatrix caelus_fdm::ecef2ned(const double L, const double l){

    return rotateAroundAxisByAngle(l+M_PI/2.,2).eval() *
           rotateAroundAxisByAngle(L,3).transpose().eval();
}

RotationMatrix caelus_fdm::ned2ecef(const double L, const double l){
    return ecef2ned(L,l).transpose().eval();
}

RotationMatrix caelus_fdm::body2wind(const State &x){
    double alpha, beta;
    alpha = atan(x[5] / x[3]);
    beta = asin(x[4] / sqrt(x[3] * x[3] + x[4] * x[4] + x[5] * x[5]));

    return rotateAroundAxisByAngle(beta,3) *
           rotateAroundAxisByAngle(alpha,2);
}

RotationMatrix caelus_fdm::wind2body(const State &x){
    return body2wind(x).transpose().eval();
}

RotationMatrix caelus_fdm::body2earth(const State &x)
{
    auto phi = x[6], theta = x[7], psi = x[8];
    return rotateAroundAxisByAngle(psi,3) *
            rotateAroundAxisByAngle(theta,2) *
            rotateAroundAxisByAngle(phi,1);
}

RotationMatrix caelus_fdm::earth2body(const State &x)
{
    return body2earth(x).transpose().eval();
}

RotationMatrix caelus_fdm::rotateAroundAxisByAngle(double angle, unsigned int axis)
{
    if (axis<=0 || axis>3)
        caelusfdm_throw("axis should be between 1 and 3");

    RotationMatrix rot(3,3);
    auto cang = cos(angle), sang = sin(angle);
    switch (axis)
    {
        case 1:
            rot <<  1, 0,     0,
                    0, cang, -sang,
                    0, sang,  cang;
            break;
        case 2:
            rot <<  cang, 0, sang,
                    0,    1, 0,
                    -sang, 0, cang;
            break;
        case 3:
            rot <<  cang, -sang, 0,
                    sang,  cang, 0,
                    0,     0,    1;
            break;
        default:
            caelusfdm_throw("axis should be between 1 and 3");
    }
    return rot;
}

void caelus_fdm::convertLlA2State(const double &L, const double &l, const double &h, State &x){

    Eigen::VectorXd R(3);
    R(0) = h*cos(l)*cos(L);
    R(1) = h*cos(l)*sin(L);
    R(2) = h*sin(l);
    x.segment(0,3) = ecef2ned(L,l)*R;

}

void caelus_fdm::convertState2LlA(const double L_in, const double l_in, const State &x, double &Lf, double &lf, double &h){

    Eigen::VectorXd R(3);
    R(0) = 0;
    R(1) = 0;
    R(2) = -R0;
    Eigen::VectorXd Xecef = ned2ecef(L_in,l_in)*(R+x.segment(0,3));
    double Xecef_norm = Xecef.norm();

    h = Xecef_norm - R0;
    Lf = atan2(Xecef[1],Xecef[0]);
    lf = asin(Xecef[2]/Xecef_norm);

}


void caelus_fdm::convertECEF2LlH(const double xECEF, const double yECEF, const double zECEF, double &L, double &phi, double &H ) {

    double a = 6377563.396, b = 6356256.909, e2, mu;
    double p = sqrt(xECEF*xECEF + yECEF*yECEF);
    e2 = (a*a - b*b)/(a*a);

    L = atan2(yECEF,xECEF);

    //Iterative procedure to compute phi
    double phiold = 0., phinew = 1.e6, eps = 1e-10;
    int count = 0;
    phiold = atan2(zECEF,(p*(1-e2)));

    while ( abs(phinew - phi) > eps && count < 1000 ){
        mu = a/sqrt(1-e2*sin(phiold)*sin(phiold));
        phinew = atan2(zECEF+e2*mu*sin(phiold),p);
        phi = phiold;
        phiold = phinew;
        count++;
    }

    if ( count == 1000) cout << "WARNING: Latitude might be inaccurate" << endl;
    phi = phinew;
    mu = a/sqrt(1-e2*sin(phi)*sin(phi));

    H = p/cos(phi) - mu;

}


void caelus_fdm::convertLl2EN(const double L, const double phi, double &E, double &N) {

    double a = 6377563.396, b = 6356256.909, e2;
    double F0 = 0.9996012717, N0 = -100000., E0 = 400000.;
    double L0 = -2.*M_PI/180.;
    double phi0 = 49.*M_PI/180.;
    e2 = (a*a - b*b)/(a*a);


    double n = (a - b)/(a + b);
    double ni = a*F0*pow(1 - e2*sin(phi)*sin(phi),-0.5);
    double rho = a*F0*(1 - e2)*pow(1 - e2*sin(phi)*sin(phi),-1.5);
    double eta2 = ni/rho -1.;

    double M = b*F0*( (1.+n+5./4.*n*n+5./4.*n*n*n)*(phi-phi0) -
                      (3.*n+3.*n*n+21./8.*n*n*n)*sin(phi-phi0)*cos(phi+phi0)
                      + (15./8.*n*n+15./8.*n*n*n)*sin(2.*(phi-phi0))*cos(2.*(phi+phi0))
                      - 35./24.*n*n*n*sin(3.*(phi-phi0))*cos(3.*(phi+phi0)));

    double I = M + N0;
    double II = ni/2.*sin(phi)*cos(phi);
    double III = ni/24.*sin(phi)*pow(cos(phi),3.)*(5.-tan(phi)*tan(phi)+9.*eta2);
    double IIIA = ni/720.*sin(phi)*pow(cos(phi),5.)*(61.-58.*tan(phi)*tan(phi)+pow(tan(phi),4.));
    double IV = ni*cos(phi);
    double V = ni/6.*pow(cos(phi),3.)*(ni/rho-tan(phi)*tan(phi));
    double VI = ni/120.*pow(cos(phi),5.)*(5.-18.*tan(phi)*tan(phi)+pow(tan(phi),4.)+14.*eta2-58.*eta2*tan(phi)*tan(phi));

//    cout << "ni = " << scientific << setprecision(10) << ni << endl;
//    cout << "rho = " << scientific << setprecision(10) << rho << endl;
//    cout << "eta2 = "<< scientific << setprecision(10) << eta2 << endl;
//    cout << "M = "<< scientific << setprecision(10) << M << endl;
//    cout << "I = " << scientific << setprecision(10)<< I << endl;
//    cout << "II = " << scientific << setprecision(10)<< II << endl;
//    cout << "III = " << scientific << setprecision(10)<< III << endl;
//    cout << "IIIA = " << scientific << setprecision(10)<< IIIA << endl;
//    cout << "IV = " << scientific << setprecision(10)<< IV << endl;
//    cout << "V = " << scientific << setprecision(10)<< V << endl;
//    cout << "VI = " << scientific << setprecision(10)<< VI << endl;

    N = I + II*(L-L0)*(L-L0) + III*pow(L-L0,4.) + IIIA*pow(L-L0,6.);
    E = E0 + IV*(L-L0) + V*pow((L-L0),3.) + VI*pow((L-L0),5.);
}


void caelus_fdm::convertLlH2ECEF(const double L, const double phi, const double H, double &xECEF, double &yECEF, double &zECEF ) {
    double a = 6377563.396, b = 6356256.909, e2, ni;
    e2 = (a*a - b*b)/(a*a);
    ni = a/sqrt(1-e2*sin(phi)*sin(phi));

    xECEF = (ni+H)*cos(phi)*cos(L);
    yECEF = (ni+H)*cos(phi)*sin(L);
    zECEF = ((1-e2)*ni+H)*sin(phi);
}