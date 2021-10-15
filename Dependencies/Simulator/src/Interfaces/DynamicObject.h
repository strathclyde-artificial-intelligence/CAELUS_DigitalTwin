#ifndef __DYNAMICOBJECT_H__
#define __DYNAMICOBJECT_H__

#include <array>
#include <Eigen/Eigen>
#include <boost/numeric/odeint.hpp>
#include <random>

#include "EnvironmentObject.h"
#include "../ClassExtensions/Aerodynamics_Extension.h"
#include "../ForceModels/ThrustQuadrotor.h"
#include "../ForceModels/Drag.h"
#include "../ForceModels/Weight.h"
#include "../ClassExtensions/ThrustFixedWing_Extension.h"
#include "../Helpers/constants.h"
#include "../Helpers/angleRateRotationMatrix.h"
#include "Clock.h"

typedef boost::numeric::odeint::runge_kutta_dopri5<Eigen::VectorXd,double,Eigen::VectorXd,double,boost::numeric::odeint::vector_space_algebra> ODESolver;

#define DYNAMIC_OBJECT_STATE_SIZE 12
#define ZEROVEC(x) Eigen::VectorXd::Zero(x)


__attribute__((unused)) static void pp_state(const Eigen::VectorXd state) {
    double s[12] = {0};
    for (int i = 0; i < 12; i++) s[i] = state.data()[i];
    std::cout << "<==========" << std::endl;
    std::cout << "X:" << s[0] << ", Y:" << s[1] << ", Z:" << s[2] << std::endl; 
    std::cout << "Xdot: " << s[3] << ", Ydot: " << s[4] << ", Zdot: " << s[5] << std::endl;
    std::cout << "Phi:" << s[6] << ", Theta:" << s[7] << ", Psy:" << s[8] << std::endl; 
    std::cout << "Phidot:" << s[9] << ", Thetadot:" << s[10] << ", Psydot:" << s[11] << std::endl; 
    std::cout << "==========>" << std::endl;
}

struct DynamicObject : public EnvironmentObject {

protected:

    double ground_height = 0;
    
    DroneConfig config;

    caelus_fdm::Weight weight_force_m;
    ThrustFixedWing fixed_wing_thrust_m;
    caelus_fdm::ThrustQuadrotor quadrotor_thrust_m;
    caelus_fdm::Drag drag_m;
    Aerodynamics hor_flight_aero_force_m;
    Clock& clock;

    ODESolver dynamics_solver;
    
    bool compute_quadrotor_dynamics = true;
    bool compute_fixed_wing_dynamics = false;
    bool compute_aero_dynamics = false;
    bool compute_weight_dynamics = true;
    bool compute_drag_dynamics = false;

    Eigen::Matrix3d moment_of_inertia;
     
    /**
     * Drone state as populated by the CAELUS_FDM package.
     * <
     *  x , y , z    [0:3]  vehicle origin with respect to earth-frame (NED m) (ENU when earth)
     *  u, v, w      [3:6]  body-frame velocity (m/s)
     *  ɸ , θ , ѱ    [6:9]  (roll, pitch, yaw) orientation with respect to earth-frame (rad)
     *  p, q, r      [9:12] body-frame orientation velocity (rad/s)
     * >
     */
    Eigen::VectorXd state{DYNAMIC_OBJECT_STATE_SIZE};
    /**
     *  (FixedWingEOM.h:evaluate)
     *  Drone state derivative as populated by the CAELUS_FDM package.
     *  ẋ , ẏ , ż       [0:3]  earth-frame velocity (NED)
     *  u., v., w.      [3:6]  body-frame acceleration (m/s**2)
     *  ɸ. , θ. , ѱ.    [6:9]  earth-frame angle rates (Euler rates)
     *  p. , q. , r.    [9:12] body-frame angular acceleration (What unit?)
     */
    Eigen::VectorXd dx_state{DYNAMIC_OBJECT_STATE_SIZE};

    void step_dynamics(
        boost::chrono::microseconds us,
        const Eigen::VectorXd& state,
        Eigen::VectorXd& dx_state) {
        
        Eigen::Vector3d total_forces = this->get_forces();
        Eigen::Vector3d total_momenta = this->get_moements();

        Eigen::Vector3d Vb = state.segment(3,3);
        Eigen::Vector3d wb = state.segment(9,3);

        dx_state = Eigen::VectorXd::Zero(12);

        dx_state.segment(0,3) = caelus_fdm::body2earth(state)*Vb;
        dx_state.segment(3,3)  = total_forces/this->weight_force_m.get_mass(); // external forces
        
        dx_state.segment(3,3) -= wb.cross(Vb.eval()); // account for frame dependent acc
        // earth-frame angle rates
        dx_state.segment(6,3) = caelus_fdm::angularVelocity2eulerRate(state)*wb;
        // body-frame angular acceleration
        
        dx_state.segment(9,3)  = total_momenta; // external torques
        dx_state.segment(9,3) -= wb.cross( this->moment_of_inertia*wb.eval() ); // account for frame dependent ang acc
        dx_state.segment(9,3)  = this->moment_of_inertia.colPivHouseholderQr().solve(dx_state.segment(9,3).eval()); // inertia matrix into account

        // Remove numerical noise < 1e-12
        for (auto i = 0; i < dx_state.size(); i++)
            dx_state[i] = fabs(dx_state[i]) < 1e-12 ? 0 : dx_state[i];
    }

    void integration_step(boost::chrono::microseconds us) {
        // Integrate using ODESolver
        double dt = us.count() / 1000000.0; // Microseconds to seconds
        this->dynamics_solver.do_step(
            [this, us] (const Eigen::VectorXd & x, Eigen::VectorXd &dx, __attribute__((unused)) const double t ) -> void
            {
                this->step_dynamics(us, x, dx);
            },
            this->state,
            this->dx_state,
            this->clock.get_current_time_us().count() / 1000000.0, // Simulation time here in seconds?
            dt
        );
    }

    void initialise_state() {
        this->state = Eigen::VectorXd::Zero(DYNAMIC_OBJECT_STATE_SIZE);
    }

    void initialise_dx_state() {
        this->dx_state = Eigen::VectorXd::Zero(DYNAMIC_OBJECT_STATE_SIZE);
    }

public:

    DynamicObject(DroneConfig config, Clock& clock) : 
        config(config),
        weight_force_m(caelus_fdm::Weight{config, G_FORCE}),
        fixed_wing_thrust_m(ThrustFixedWing{config}),
        quadrotor_thrust_m(caelus_fdm::ThrustQuadrotor{config}),
        hor_flight_aero_force_m(Aerodynamics{config}),
        drag_m(caelus_fdm::Drag{config}),
        clock(clock)
        {
            this->initialise_state();
            this->initialise_dx_state();
            this->moment_of_inertia = config.J;
        };

    ~DynamicObject() {};

    Eigen::VectorXd& get_vector_state() { return this->state; }
    Eigen::VectorXd& get_vector_dx_state() { return this->dx_state; }
    
    Eigen::Vector3d get_forces() {
        Eigen::Vector3d fixed_wing_force = this->compute_fixed_wing_dynamics ? this->fixed_wing_thrust_m.getF() : ZEROVEC(3);
        Eigen::Vector3d quadrotor_force = this->compute_quadrotor_dynamics ? this->quadrotor_thrust_m.getF() : ZEROVEC(3);
        Eigen::Vector3d aero_force = this->compute_aero_dynamics ? this->hor_flight_aero_force_m.getF() : ZEROVEC(3);
        Eigen::Vector3d weight_force = this->compute_weight_dynamics ? this->weight_force_m.getF() : ZEROVEC(3);
        Eigen::Vector3d drag_force = this->compute_drag_dynamics ? this->drag_m.getF() : ZEROVEC(3);
        return fixed_wing_force + quadrotor_force + aero_force + weight_force + drag_force;
    }

    Eigen::Vector3d get_moements() {
        Eigen::Vector3d fixed_wing_moment = this->compute_fixed_wing_dynamics ? this->fixed_wing_thrust_m.getM() : ZEROVEC(3);
        Eigen::Vector3d quadrotor_moment = this->compute_quadrotor_dynamics ? this->quadrotor_thrust_m.getM() : ZEROVEC(3);
        Eigen::Vector3d aero_moment = this->compute_aero_dynamics ? this->hor_flight_aero_force_m.getM() : ZEROVEC(3);
        Eigen::Vector3d weight_moment = this->compute_weight_dynamics ? this->weight_force_m.getM() : ZEROVEC(3);
        Eigen::Vector3d drag_moment = this->compute_drag_dynamics ? this->drag_m.getM() : ZEROVEC(3);

        return fixed_wing_moment + quadrotor_moment + aero_moment + weight_moment + drag_moment;
    }

    void update(boost::chrono::microseconds us) override {
        Eigen::VectorXd state = this->get_vector_state();
        if (this->compute_fixed_wing_dynamics)
            this->fixed_wing_thrust_m.updateParamsImpl(0,state);
        if (this->compute_quadrotor_dynamics)
            this->quadrotor_thrust_m.updateParamsImpl(0,state);
        if (this->compute_aero_dynamics)
            this->hor_flight_aero_force_m.updateParamsImpl(0,state);
        if (this->compute_weight_dynamics)
            this->weight_force_m.updateParamsImpl(0,state);
        this->integration_step(us);
    }

    void setControllerVTOL(std::function<Eigen::VectorXd(double)> controller) {
        this->quadrotor_thrust_m.setController(controller);
    }

    void setControllerThrust(std::function<Eigen::VectorXd(double)> controller) {
        this->fixed_wing_thrust_m.setController(controller);
    }

    void setControllerAero(std::function<Eigen::VectorXd(double)> controller) {
        this->hor_flight_aero_force_m.setController(controller);
    }

    void set_fake_ground_level(double level) {
        this->ground_height = level;
    }
};

#endif // __DYNAMICOBJECT_H__