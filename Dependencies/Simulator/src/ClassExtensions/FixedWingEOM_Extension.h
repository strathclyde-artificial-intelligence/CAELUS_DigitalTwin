#ifndef __FIXEDWINGEOM_EXTENSION_H__
#define __FIXEDWINGEOM_EXTENSION_H__

#include <EquationsOfMotion/FixedWingEOM.h>
#include "../Containers/DroneConfig.h"

class FixedWingEOM : public caelus_fdm::FixedWingEOM {
public:
    FixedWingEOM(DroneConfig conf) : caelus_fdm::FixedWingEOM(
        conf.b_prop,
        conf.c,
        conf.b_aero,
        conf.S,
        conf.drone_aero_config,
        conf.J,
        NULL,
        conf.mass,
        9.81
    ) {}

    void print_vec(Eigen::VectorXd e) {
        for (int i = 0; i < e.size(); i++) printf("%f ", e[i]);
        printf("\n");
    }

//     int evaluate(const double &t, const caelus_fdm::State &x, caelus_fdm::StateDerivative &dx) override {
//         {
//             using namespace caelus_fdm;
//             // body frame linear and angular velocity
//             Eigen::Vector3d Vb = x.segment(3,3);
//             Eigen::Vector3d wb = x.segment(9,3);

//             printf("t: %f\n", t);
//             this->print_vec(x);


//             // evaluate forces and torques
//             Force  f_a, f_g; //not in body frame
//             m_weightFM.updateParamsImpl(t,x);
//             m_thrustFM.updateParamsImpl(t,x);
//             m_AeroFM.updateParamsImpl(t,x);
            
//             f_g = m_weightFM.getF();
//             printf("Force: ");
//             this->print_vec(f_g);
//             f_a = m_AeroFM.getF();
//             printf("Force2: ");
//             this->print_vec(f_a);
//             m_ft = m_thrustFM.getF();
//             printf("Force3: ");
//             this->print_vec(m_ft);

//             std::exit(0);
            
//             m_mg = m_weightFM.getM();
//             m_ma = m_AeroFM.getM();
//             m_mt = m_thrustFM.getM();


//             // Forces that need rotation (mass, aero)
//             m_fg = earth2body(x)*f_g;
//             m_fa = wind2body(x)*f_a;

// //            m_ft[0] = -m_fa[0]*m_thrustFM.get_controller_prop(t)[0];

//             // assign output
//             dx = StateDerivative(x.size());

//             // earth-frame velocity
//             dx.segment(0,3) = body2earth(x)*Vb;

//             // body-frame acceleration
//             dx.segment(3,3)  = (m_ft+m_fg+m_fa)/m_weightFM.get_mass(); // external forces
// //            dx.segment(3,3) -= wb.cross(Vb); // account for frame dependent acc

//             // earth-frame angle rates
//             dx.segment(6,3) = angularVelocity2eulerRate(x)*wb;

//             // body-frame angular acceleration
//             dx.segment(9,3)  = m_mt+m_ma; // external torques
//             dx.segment(9,3) -= wb.cross( m_I*wb.eval() ); // account for frame dependent ang acc
//             dx.segment(9,3)  = m_I.colPivHouseholderQr().solve(dx.segment(9,3).eval()); // inertia matrix into account

//             return 0;
//         }        
//     }
};

#endif // __FIXEDWINGEOM_EXTENSION_H__