#include "Drone.h"
#include "Logging/ConsoleLogger.h"

// #define HIL_ACTUATOR_CONTROLS_VERBOSE

DroneConfig config_from_file_path(char* path) {
    DroneConfig conf;
    std::ifstream fin(path);
    fin >> conf;
    return conf;
}

void pp_state(const Eigen::VectorXd state) {
    double s[12] = {0};
    for (int i = 0; i < 12; i++) s[i] = state.data()[i];
    std::cout << "<==========" << std::endl;
    std::cout << "X:" << s[0] << ", Y:" << s[1] << ", Z:" << s[2] << std::endl; 
    std::cout << "Xdot: " << s[3] << ", Ydot: " << s[4] << ", Zdot: " << s[5] << std::endl;
    std::cout << "Phi:" << s[6] << ", Theta:" << s[7] << ", Psy:" << s[8] << std::endl; 
    std::cout << "Phidot:" << s[9] << ", Thetadot:" << s[10] << ", Psydot:" << s[11] << std::endl; 
    std::cout << "==========>" << std::endl;
}

Drone::Drone(char* config_file, MAVLinkMessageRelay& connection) : 
    MAVLinkSystem::MAVLinkSystem(1, 1),
    state(STATE_SIZE),
    dx_state(STATE_SIZE),
    config(config_from_file_path(config_file)),
    dynamics(config),
    dynamics_solver(),
    connection(connection)
    {
        this->connection.add_message_handler(this);
        this->_setup_drone();
        for (int i = 0; i < STATE_SIZE; i++) {
            this->state[i] = 0;
            this->dx_state[i] = 0;
        } 
        // This is a hack, please check with Gianluca what's going on.
        // If state[3] is initialised to 0 the ODE solver populates the state with nan(s).
        this->state[3] = 0.0001; 
    }

void Drone::_setup_drone() {
    // Inject controllers into dynamics model
    this->dynamics.setController([this] (double dt) -> Eigen::VectorXd
        { return this->thrust_propellers.control(dt); });
    this->dynamics.setControllerAero([this] (double dt) -> Eigen::VectorXd
        { return this->ailerons.control(dt); });
    this->dynamics.setControllerVTOL([this] (double dt) -> Eigen::VectorXd
        { return this->vtol_propellers.control(dt); });
}

void Drone::update(boost::chrono::microseconds us) {
    MAVLinkSystem::update(us);
    this->_process_mavlink_messages();
    this->_step_dynamics(us);
    this->_publish_state(us);
}

void fake_ground_transform(
                        Eigen::VectorXd& state,
                        float dt) {
    printf("Delta t %f\n", dt);
    state[2] = 0;
}

void Drone::_step_dynamics(boost::chrono::microseconds us) {
    Eigen::VectorXd new_state{12};
    Eigen::VectorXd new_dx_state{12};
    
    double time_old = this->get_sim_time() / 1000; // to ms
    double time_new = 0;

    // this->dynamics_solver.do_step_impl(
    //     [this] (const Eigen::VectorXd & x, Eigen::VectorXd &dx, const double t) -> void
    //             {
    //                 this->dynamics.evaluate(t,x,dx);
    //             }
    //     ,
    //     new_state,
    //     new_dx_state,
    //     time_old, 
    //     new_state,
    //     new_dx_state,
    //     us.count() / 2000000.0 // us to sec
    // );

    // time_new = time_old + (us.count() / 2000000.0);

    // this->dynamics_solver.do_step_impl(
    //     [this] (const Eigen::VectorXd & x, Eigen::VectorXd &dx, const double t) -> void
    //             {
    //                 this->dynamics.evaluate(t,x,dx);
    //             }
    //     ,
    //     new_state,
    //     new_dx_state,
    //     time_new, // to ms
    //     new_state,
    //     new_dx_state,
    //     us.count() / 2000000.0 // us to sec
    // );

    // time_new = time_old + (us.count() / 2000000.0);

    // this->dynamics_solver.calc_state(
    //     time_new,
    //     new_state,
    //     this->state,
    //     this->dx_state,
    //     time_old,
    //     new_state,
    //     new_dx_state,
    //     time_new
    // );

    // STALL DETECTION SHOULD NOT HAPPEN DURING VTOL
    // fake_ground_transform(new_dx_state, us.count() / 1000000.0f);
    double dt = us.count() / 1000000.0;
    this->dynamics_solver.do_step(
        [this, dt] (const Eigen::VectorXd & x, Eigen::VectorXd &dx, const double t) -> void
        {
            this->dynamics.evaluate(t,x,dx);
            this->dx_state = dx;
        },
        this->state,
        this->get_sim_time() / 1000,
        new_state,
        dt
    );

    // FAKE GROUND
    if (new_state[2] > -0.01)
        new_state[5] += (G_FORCE * dt);

    for ( auto i = 0; i < new_state.size(); i++ )
        if (std::fabs(new_state(i))<=1.e-4)
            new_state(i) = 0.;
    for ( auto i = 0; i < dx_state.size(); i++ )
        if (std::fabs(dx_state(i))<=1.e-4)
            dx_state(i) = 0.;
    
    // printf("Velocity x: %f y: %f z: %f\n", new_state[3], new_state[4], new_state[5]);
    
    this->state = new_state;
}

MAVLinkMessageRelay& Drone::get_mavlink_message_relay() {
    return this->connection;
}

void Drone::_publish_hil_gps() {
    this->connection.enqueue_message(
        this->hil_gps_msg(this->system_id, this->component_id)
    );
}

void Drone::_publish_system_time() {
    this->connection.enqueue_message(
        this->system_time_msg(this->system_id, this->component_id)
    );
}

void Drone::_publish_hil_sensor() {
    this->connection.enqueue_message(this->hil_sensor_msg(this->system_id, this->component_id));
}

void Drone::_publish_hil_state_quaternion() {
    mavlink_message_t msg = this->hil_state_quaternion_msg(this->system_id, this->component_id);
    this->connection.enqueue_message(msg);
}

void Drone::_publish_state(boost::chrono::microseconds us)
 {
    if (!this->connection.connection_open()) return;
    if (!(this->should_reply_lockstep || this->hil_actuator_controls_msg_n < 300)) return;

    // TODO: move time computation up a layer
    this->time += us;
    this->_publish_hil_gps();
    this->_publish_hil_sensor();
    this->should_reply_lockstep = false;

    bool should_send_autopilot_telemetry = 
        (this->time - this->last_autopilot_telemetry).count()
        > this->hil_state_quaternion_message_frequency;
    
    if (!should_send_autopilot_telemetry) return;
    
    this->last_autopilot_telemetry = this->time;
    
    this->_publish_hil_state_quaternion();

    if (this->sys_time_throttle_counter++ % 1000) {
        this->_publish_system_time();
    }
}

/**
 * Process a MAVLink command.
 * Correct command receival must be ACK'ed.
 * 
 */
void Drone::_process_command_long_message(mavlink_message_t m) {
    mavlink_command_long_t command;
    mavlink_message_t command_ack_msg;
    mavlink_msg_command_long_decode(&m, &command);
    uint16_t command_id = command.command;
    
    switch(command_id) {
        case MAV_CMD_SET_MESSAGE_INTERVAL:
            printf("Simulator -> PX4 message interval now set to %f (us)\n", command.param2);
            this->hil_state_quaternion_message_frequency = command.param2;
            break;
        default:
            fprintf(stdout, "Unknown command id from command long (%d)", command_id);
    }
    
    mavlink_msg_command_ack_pack(this->system_id, this->component_id, &command_ack_msg, command_id, 0, 0, 0, command.target_system, command.target_component);
    this->connection.enqueue_message(command_ack_msg);
}

void Drone::_process_hil_actuator_controls(mavlink_message_t m) {
    
    this->should_reply_lockstep = true;
    this->hil_actuator_controls_msg_n++;

    mavlink_hil_actuator_controls_t controls;
    mavlink_msg_hil_actuator_controls_decode(&m, &controls);
    this->armed = (controls.mode & MAV_MODE_FLAG_SAFETY_ARMED) > 0;
    //this->mav_mode = controls.mode;
    
    Eigen::VectorXd vtol_prop_controls{4};
    for (int i = 0; i < 4; i++) vtol_prop_controls[i] = controls.controls[i];
    Eigen::VectorXd ailerons_controls{2};
    for (int i = 0; i < 2; i++) ailerons_controls[i] = controls.controls[4+i];
    Eigen::VectorXd thrust_propeller_controls{1};
    for (int i = 0; i < 1; i++) thrust_propeller_controls[i] = controls.controls[8+i];

#ifdef HIL_ACTUATOR_CONTROLS_VERBOSE
    printf("HIL_ACTUATOR_CONTROLS:\n");
    for (int i = 0; i < 16; i++) {
        printf("\tControl #%d: %f\n", i, controls.controls[i]);
    } printf("\n");
#endif

    this->thrust_propellers.set_control(thrust_propeller_controls);
    this->ailerons.set_control(ailerons_controls);
    this->vtol_propellers.set_control(vtol_prop_controls);
    
}

void Drone::_process_mavlink_message(mavlink_message_t m) {
    ConsoleLogger* logger = ConsoleLogger::shared_instance();
    switch(m.msgid) {
        case MAVLINK_MSG_ID_HEARTBEAT:
            logger->debug_log("MSG: HEARTBEAT");
            break;
        case MAVLINK_MSG_ID_HIL_ACTUATOR_CONTROLS:
            logger->debug_log("MSG: HIL_ACTUATOR_CONTROLS");
            this->_process_hil_actuator_controls(m);
            break;
        case MAVLINK_MSG_ID_COMMAND_LONG:
            logger->debug_log("MSG: COMMAND_LONG");
            this->_process_command_long_message(m);
            break;
        default:
            logger->debug_log("Unknown message!");
    }
}

void Drone::_process_mavlink_messages() {
    this->message_queue.consume_all([this](mavlink_message_t m){
        this->_process_mavlink_message(m);
    });
}

void Drone::handle_mavlink_message(mavlink_message_t m) {
    this->message_queue.push(m);
}

#pragma mark DroneStateEncoder

uint64_t Drone::get_sim_time() {
    return this->time.count();
}

Eigen::VectorXd& Drone::get_vector_state() {
    return this->state;
}

Eigen::VectorXd& Drone::get_vector_dx_state() {
    return this->dx_state;
}

Eigen::Vector3d Drone::get_environment_wind() {
    Eigen::Vector3d wind = Eigen::Vector3d::Zero(3);
    return wind;
}

float Drone::get_temperature_reading() {
    return 25.0;
}

uint8_t Drone::get_mav_mode() {
    return this->mav_mode;
}