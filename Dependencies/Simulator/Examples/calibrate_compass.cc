#include "../src/Sim6DOFInfo.h"
#include "../src/Logging/ConsoleLogger.h"
#include "../src/Simulator.h"
#include "../src/Drone.h"
#include "../src/Logging/GodotRouter.h"
#include "../src/Drone.h"
#include <boost/thread.hpp>
#include "../src/Sockets/MAVLinkConnectionHandler.h"
#include <Eigen/Eigen>
#include <thread>
#include <functional> 

#define DEG_RAD 0.01745

struct Attitude {
    double roll;
    double pitch;
    double yaw;
};

class HandledDrone : public Drone {
private: 
    std::vector<Attitude> poses;
    int current_pose_idx = 0;
    Eigen::VectorXd rotation_vec{3};
public:
    HandledDrone(const char* config_file, MAVLinkMessageRelay& connection, Clock& clock) : 
    Drone(config_file, connection, clock) {
        rotation_vec[0] = 0;
        rotation_vec[1] = 0;
        rotation_vec[2] = -0.5;
        this->rotation_vec = rotation_vec;
        this->poses.push_back(Attitude{0.0, 0.0, 0});
        this->poses.push_back(Attitude{90*DEG_RAD, 0.0, 0});
        this->poses.push_back(Attitude{180*DEG_RAD, 0.0, 0});
        this->poses.push_back(Attitude{-90*DEG_RAD, 0.0, 0});
        this->poses.push_back(Attitude{0.0, 90*DEG_RAD, 0});
        this->poses.push_back(Attitude{0.0, -90*DEG_RAD, 0});
    }

    void update(boost::chrono::microseconds us) override;
    void fake_handling_transform() {
        Attitude current_pose = this->poses[(int)floor(this->current_pose_idx / 2)];
        Eigen::VectorXd pose_vec{3};
        pose_vec[0] = current_pose.roll;
        pose_vec[1] = current_pose.pitch;
        pose_vec[2] = current_pose.yaw;

        if (this->current_pose_idx % 2 == 0) {
            this->state.segment(9,3) = Eigen::VectorXd::Zero(3);
            this->dx_state.segment(6,3) = Eigen::VectorXd::Zero(3);
            this->state.segment(6,3) = pose_vec;
        } else {
            this->state.segment(9,3) = caelus_fdm::earth2body(this->state) * this->rotation_vec;
            this->dx_state.segment(6,3) = this->rotation_vec;
        }
    }

    void fake_ground_transform(boost::chrono::microseconds us) {
        double dt = (us.count() / 1000000.0);
        Eigen::Vector3d position = this->get_sensors().get_earth_frame_position(); // NED
        Eigen::Vector3d velocity = this->get_sensors().get_earth_frame_velocity(); // NED
        Eigen::Vector3d acceleration = caelus_fdm::body2earth(this->state) * this->get_sensors().get_body_frame_acceleration();

        if (position[2] >= this->ground_height && acceleration[2] * dt + velocity[2] >= 0) {
            this->state[2] = 0;
            this->state.segment(3, 3) = Eigen::VectorXd::Zero(3);
        }
    }

    void next_pose() {
        this->current_pose_idx = (this->current_pose_idx+1) % (this->poses.size() * 2);
    }
};

void HandledDrone::update(boost::chrono::microseconds us) {
    this->_process_mavlink_messages();

    if (this->hil_actuator_controls_msg_n > 300 && !this->should_reply_lockstep) return;
    MAVLinkSystem::update(us);
    DynamicObject::update(us);
    this->fake_handling_transform();
    this->fake_ground_transform(us);
    this->_publish_state(us);

    if (this->drone_state_processor != NULL) {
        this->drone_state_processor->new_drone_state(this->state, this->dx_state);
    }
}


int main()
{

    std::cout << "6 DOF Simulator" << std::endl;

    const char* fixed_wing_config = "../drone_models/small";
    ConsoleLogger* cl = ConsoleLogger::shared_instance();
    cl->set_debug(false);
    
    boost::asio::io_service service;
    boost::asio::io_service godot_service;

    MAVLinkConnectionHandler handler{service, ConnectionTarget::PX4};
    boost::thread link_thread = boost::thread(boost::bind(&boost::asio::io_service::run, &service));
    std::shared_ptr<Simulator> s(new Simulator({4000, 2, true}));
    GodotRouter r{godot_service, s->simulation_clock};
    
    HandledDrone d{fixed_wing_config, handler, s->simulation_clock };
    d.set_fake_ground_level(0);
    d.set_drone_state_processor(*s);
    s->add_environment_object(d);
    s->add_drone_state_processor(&r);

    std::thread t1([s] () { s->start(); });
    
    while(1) {
        char buff[10] = {0};
        std::cout << ">>> ";
        scanf("%c", &buff);
        d.next_pose();
    }
    t1.join();

    return 0;
}
