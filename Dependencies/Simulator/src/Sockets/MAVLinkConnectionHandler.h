#ifndef __MAVLINKCONNECTIONHANDLER_H__
#define __MAVLINKCONNECTIONHANDLER_H__

#include <boost/asio.hpp>
#include <boost/signals2/signal.hpp>
#include "../Interfaces/MAVLinkMessageHandler.h"
#include "TCPAcceptor.h"
#include "../Interfaces/MAVLinkMessageRelay.h"

#define MAX_MAVLINK_PACKET_LEN 512

using namespace boost::asio;

enum ConnectionTarget {
    PX4 = 4560
};

class MAVLinkConnectionHandler : 
    public MAVLinkMessageRelay,
    public DataReceiver,
    public DataSender {
private:
    char mavlink_msg_buffer[MAX_MAVLINK_PACKET_LEN];
    uint buffer_read_head = 0;
    uint buffer_parse_head = 0;
    TCPAcceptor tcp_acceptor;
    boost::signals2::signal<void(mavlink_message_t)> new_message_signal;
    std::vector<MAVLinkMessageHandler*> message_handlers;
    bool parse_mavlink_message(const char* buff, size_t len, mavlink_message_t& msg, mavlink_status_t& status);
    bool send_message(const mavlink_message_t& m) override;
public:
    MAVLinkConnectionHandler(io_service& service, ConnectionTarget target);    
    ~MAVLinkConnectionHandler();
    void add_message_handler(MAVLinkMessageHandler* h) override;
    void handle_mavlink_message(mavlink_message_t m);
    void receive_data(const char* buff, size_t len) override;
    size_t send_data(const void* buff, size_t len) override;
    bool received_message(mavlink_message_t m) override;
    void enqueue_message(mavlink_message_t m) override;
    bool connection_open() override;
};

#endif // __MAVLINKCONNECTIONHANDLER_H__