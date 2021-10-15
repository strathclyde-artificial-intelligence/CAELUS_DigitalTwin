/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */
/*
------ Copyright (C) 2021 University of Strathclyde and Authors ------
-------------------- e-mail: gaetano.pascarella@strath.ac.uk ---------
----------------------- Author: Gaetano Pascarella -------------------
*/

#ifndef CAELUS_FDM_AERODYNAMICS_H
#define CAELUS_FDM_AERODYNAMICS_H

#include "BaseFM.h"
#include "../Helpers/constants.h"

namespace caelus_fdm {

    using namespace std;

    struct APM {

        // Force and Moments coefficients at rest
        double m_CD_0 = 0., m_CS_0 = 0., m_CL_0 = 0.; //!< \brief Resultant Aerodynamic Forces Coefficients clean configuration
        double m_Cl_0 = 0., m_Cm_0 = 0., m_Cn_0 = 0.; //!< \brief Resultant Aerodynamic Moments Coefficients clean configuration

        // Force coefficients derivatives with respect to parameters of interest
        double m_CD_alpha = 0.,m_CD_alpha2 = 0., m_CD_beta = 0., m_CD_beta2 = 0., m_CD_q = 0., m_CD_delta_e2 = 0.;
        double m_CL_alpha = 0., m_CL_q = 0., m_CL_delta_e = 0.;
        double m_CS_beta = 0., m_CS_p = 0., m_CS_r = 0., m_CS_delta_a = 0., m_CS_delta_r = 0.;

        // Moments coefficients derivatives with respect to parameters of interest
        double m_Cl_beta = 0., m_Cl_p = 0., m_Cl_r = 0., m_Cl_delta_a = 0., m_Cl_delta_r = 0.;
        double m_Cm_alpha = 0., m_Cm_delta_e = 0., m_Cm_q = 0.;
        double m_Cn_beta = 0., m_Cn_p = 0., m_Cn_r = 0., m_Cn_delta_a = 0., m_Cn_delta_r = 0.;


    };

    class Aerodynamics : public BaseFM {

    protected:

        // Attributes
        double m_alpha; //!< \brief angle of attack
        double m_beta; //!< \brief angle of sideslip
        double m_Va; //!< \brief Velocity Amplitude
        Eigen::VectorXd m_Delta; //!< \brief Aerodynamic surfaces deflection (m_Delta[0] = d_e, m_Delta[1] = d_a)

        double m_rho, m_T; //!< \brief density and temperature
        double m_c, m_b; //!< \brief Characteristic lenghts for forces and moments
        double m_S; //!< \brief Characteristic area for forces and moments

        APM m_data; //!< \brief Infos on aerodynamic performance

        // For small angles of attack CL = CL(alpha, Delta_e, q)
        double m_CD, m_CS, m_CL; //!< \brief Resultant Aerodynamic Forces Coefficients
        double m_Cl, m_Cm, m_Cn; //!< \brief Resultant Aerodynamic Moment Coefficients

        function<Eigen::VectorXd(double)> m_controller;

        int computeTrho(const State &x){
            m_rho = 1.225;
            m_T = 288.15;
            return 0;
        }

        int computeAngles(const State &x){
            m_alpha = atan2(x[5],x[3]); 
            if (m_alpha < DEG_TO_RAD * -5 || m_alpha > DEG_TO_RAD * 15) { // STALLING
                fprintf(stderr, "[WARNING] The aricraft is stalling (a.o.a: %f deg)-- maintain attitude between (-5 - +15)deg angle of attack!\n", m_alpha * RAD_TO_DEG);
                m_alpha = m_alpha < 0 ? DEG_TO_RAD * -5 : DEG_TO_RAD * 15;
            }
            m_beta = asin(x[4]/sqrt(x[3]*x[3]+x[4]*x[4]+x[5]*x[5]));
            return 0;
        }

        int computeVmod(const State &x){
            m_Va = sqrt(x[3]*x[3]+x[4]*x[4]+x[5]*x[5]);
            return 0;
        }

    public:

//        Aerodynamics() = default;

        Aerodynamics( double c, double b, double S, APM data, function<Eigen::VectorXd(double)> controller) :
            BaseFM(), m_c(c), m_b(b), m_S(S), m_data(data), m_controller(move(controller))
        {
        }

        virtual ~Aerodynamics() = default;

        double getrho(){
            return m_rho;
        }
        /**
         * Evaluate  Aerodynamic force/moment [Gryte, “Aerodynamic  modeling  of  the  Skywalker  X8  Fixed-Wing  UnmannedAerial  Vehicle”]
         * @param t : time
         * @param x : state as [ x y z ...                    body-frame origin wrt earth-frame
         *                      x_dot y_dot z_dot ...         body-frame velocity
         *                      phi theta psi ...             body-frame orientation wrt earth-frame
         *                      phi_dot theta_dot psi_dot ... body-frame orientation velocity
         *                      ]
         * @param F/M: force in wind-frame, torque in body-frame
         * @return
         */
        int computeF(const double &t, const State &x) override {

            m_CD = m_data.m_CD_0 + m_data.m_CD_alpha*m_alpha + m_data.m_CD_alpha2*m_alpha*m_alpha +
                    m_data.m_CD_delta_e2*m_Delta[0]*m_Delta[0] + m_data.m_CD_beta*m_beta +
                    m_data.m_CD_beta2*m_beta*m_beta + m_data.m_CD_q*m_c/(2.*m_Va)*x[10];
            m_CS = m_data.m_CS_0 + m_data.m_CS_beta*m_beta + m_data.m_CS_delta_a*m_Delta[1] + m_b/(2.*m_Va)*
                    (m_data.m_CS_p*x[9] + m_data.m_CS_r*x[11]);
            m_CL = m_data.m_CL_0 + m_data.m_CL_alpha*m_alpha + m_data.m_CL_delta_e*m_Delta[0] +
                    m_data.m_CL_q*m_c/(2.*m_Va)*x[10];

            m_F.resize(3);
            m_F[0] = -0.5*m_rho*m_Va*m_Va*m_S*m_CD;
            m_F[1] = 0.5*m_rho*m_Va*m_Va*m_S*m_CS;
            m_F[2] = -0.5*m_rho*m_Va*m_Va*m_S*m_CL;

            return 0;
        }

        int computeM(const double &t, const State &x) override {

            m_Cl = m_data.m_Cl_0 + m_data.m_Cl_beta*m_beta + m_data.m_Cl_delta_a*m_Delta[1] +
                    m_b/(2.*m_Va)*(m_data.m_Cl_p*x[9] + m_data.m_Cl_r*x[11]);
            m_Cm = m_data.m_Cm_0 + m_data.m_Cm_alpha*m_alpha + m_data.m_Cm_delta_e*m_Delta[0] +
                    m_data.m_Cm_q*m_c/(2.*m_Va)*x[10];
            m_Cn = m_data.m_Cn_0 + m_data.m_Cn_beta*m_beta + m_data.m_Cn_delta_a*m_Delta[1] +
                    m_b/(2.*m_Va)*(m_data.m_Cn_p*x[9] + m_data.m_Cn_r*x[11]);

            m_M.resize(3);
            m_M[0] = 0.5*m_rho*m_Va*m_Va*m_Cl*m_S*m_b;
            m_M[1] = 0.5*m_rho*m_Va*m_Va*m_Cm*m_S*m_c;
            m_M[2] = 0.5*m_rho*m_Va*m_Va*m_Cn*m_S*m_b;
            return 0;
        }

        using BaseFM::getF;
        using BaseFM::getM;
        using BaseFM::updateParams;

        int updateParamsImpl(const double &t, const State &x) override {
            this->computeTrho(x);
            this->computeAngles(x);
            this->computeVmod(x);
            m_Delta = m_controller(t);
            auto state_F = this->computeF(t,x);
            auto state_M = this->computeM(t,x);
            return 0;
        }

        int setController(function<Eigen::VectorXd(double)> controller) {
            m_controller = controller;
            return 0;
        }
    };

}

#endif //CAELUS_FDM_AERODYNAMICS_H
