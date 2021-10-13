#include "Sim6DOFInfo.h"
#include "Logging/ConsoleLogger.h"
#include "Simulator.h"
#include "Drone.h"
#include <boost/thread.hpp>
#include "Sockets/MAVLinkConnectionHandler.h"
#include <Eigen/Eigen>

int main(int argc, char const *argv[])
{

    ConsoleLogger* cl = ConsoleLogger::shared_instance();
    cl->set_debug(false);

    boost::asio::io_service service;
    MAVLinkConnectionHandler handler{service, ConnectionTarget::PX4};
    boost::thread link_thread = boost::thread(boost::bind(&boost::asio::io_service::run, &service));
    std::unique_ptr<Simulator> s(new Simulator({4000, 1, true}, handler));
    
    Drone d{"../drone_models/fixed_wing", handler};
    s->add_environment_object(d);
    s->start();
    
    return 0;
}
