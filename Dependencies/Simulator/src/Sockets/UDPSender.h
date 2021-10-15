#ifndef __UDPSENDER_H__
#define __UDPSENDER_H__

#include <boost/asio.hpp>
using namespace boost::asio;

class UDPSender {
private:
    io_service& service;
    ip::udp::socket socket;
    uint32_t throttle = 0;
public:
    UDPSender(io_service& service) : 
    service(service),
    socket(service)
    {
        this->socket.open(ip::udp::v4());
    }   

    void send_data(std::string data) {
        if (throttle++ % 15 != 0) return;
        const boost::asio::ip::udp::endpoint ep(ip::address::from_string("127.0.0.1"), 12345);
        boost::system::error_code err;
        socket.send_to(buffer(data.c_str(), data.size()), ep, 0, err);
    }
};

#endif // __UDPSENDER_H__