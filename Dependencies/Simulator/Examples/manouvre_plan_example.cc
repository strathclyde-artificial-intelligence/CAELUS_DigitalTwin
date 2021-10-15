#include "../src/Controllers/SimpleFixedWingController.h"

int main() {
    DroneConfig config = config_from_file_path("../drone_models/fixed_wing");
    std::vector<Manoeuvre> manoeuvres{Manoeuvre::CLIMB, Manoeuvre::HOLD, Manoeuvre::PITCH, Manoeuvre::HOLD};
    std::vector<boost::chrono::microseconds> section_lenghts{
        boost::chrono::microseconds{1000000 * 3}, // 3 s
        boost::chrono::microseconds{1000000 * 2}, // 2 s
        boost::chrono::microseconds{1000 * 4}, // 4ms (1 timestep)
        boost::chrono::microseconds{1000000 * 2} // 2 s
    };
    ManoeuvrePlan plan{section_lenghts, manoeuvres};
    SimpleFixedWingController quadController{config};
    quadController.set_plan(plan);

    for (auto t = boost::chrono::microseconds{0}; t < boost::chrono::seconds{static_cast<long long>(7.004)}; t+=boost::chrono::microseconds{4000}) {
        Eigen::VectorXd control = quadController.get_current_pwm_control();
        quadController.update(boost::chrono::microseconds{4000});
    }
}