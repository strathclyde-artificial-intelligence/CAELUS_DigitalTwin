
#include "../src/StandaloneDrone.h"
#include "../src/Simulator.h"
#include "../src/Controllers/SimpleFixedWingController.h"
#include "../src/Logging/GodotRouter.h"
#include <boost/thread.hpp>
#include <Eigen/Eigen>

ManoeuvrePlan* yaw(const char* config) {

    std::vector<Manoeuvre> manoeuvres{Manoeuvre::HOLD, Manoeuvre::YAW};
    std::vector<boost::chrono::microseconds> section_lenghts{
        boost::chrono::microseconds{4000}, // 4ms
        boost::chrono::microseconds{1000}, // 1 ms
    };
    return new ManoeuvrePlan{section_lenghts, manoeuvres};
}

ManoeuvrePlan* pitch(const char* config) {

    std::vector<Manoeuvre> manoeuvres{Manoeuvre::HOLD, Manoeuvre::PITCH};
    std::vector<boost::chrono::microseconds> section_lenghts{
        boost::chrono::microseconds{4000}, // 4ms
        boost::chrono::microseconds{1000 * 100}, // 12 ms (3 timesteps)
    };
    return new ManoeuvrePlan{section_lenghts, manoeuvres};
}

ManoeuvrePlan* roll(const char* config) {

    std::vector<Manoeuvre> manoeuvres{Manoeuvre::HOLD, Manoeuvre::ROLL};
    std::vector<boost::chrono::microseconds> section_lenghts{
        boost::chrono::microseconds{4000}, // 4ms
        boost::chrono::microseconds{1000}, // 12 ms (3 timesteps)
    };
    return new ManoeuvrePlan{section_lenghts, manoeuvres};
}


int main()
{
    long time_step_us{4000};
    const char* drone_config = "../drone_models/small";
    
    boost::asio::io_service godot_service;

    SimpleFixedWingController quadController{config_from_file_path(drone_config)};
    
    ManoeuvrePlan* plan = pitch(drone_config);
    quadController.set_plan(*plan);
    
    std::unique_ptr<Simulator> s(new Simulator({time_step_us, 1, false}));
    GodotRouter r{godot_service, s->simulation_clock};
    StandaloneDrone d{drone_config, s->simulation_clock, quadController};

    d.set_fake_ground_level(5);
    d.set_drone_state_processor(*s);
    s->add_environment_object(d);
    s->add_drone_state_processor(&r);
    s->start(quadController.get_total_plan_duration_us());
    
    return 0;
}
