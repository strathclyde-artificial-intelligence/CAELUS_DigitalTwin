#include "MAVLinkConnectionHandler.h"
#include "../Logging/ConsoleLogger.h"

static ConsoleLogger* c = ConsoleLogger::shared_instance();

MAVLinkConnectionHandler::MAVLinkConnectionHandler(io_service& service, ConnectionTarget target) : 
    tcp_acceptor(service, (int)target) {
        this->tcp_acceptor.add_data_receiver(this);
        this->new_message_signal.connect(boost::bind(&MAVLinkConnectionHandler::send_message, this, _1));
}

MAVLinkConnectionHandler::~MAVLinkConnectionHandler() {}

bool MAVLinkConnectionHandler::parse_mavlink_message(const char* buff, size_t len, mavlink_message_t& msg, mavlink_status_t& status) {
    for (int i = 0; i < len; i++) {
        if (mavlink_parse_char(MAVLINK_COMM_0,buff[i], &msg, &status)) return true;
    }
    return false;
}

void MAVLinkConnectionHandler::receive_data(const char* buff, size_t len) {
    mavlink_message_t msg;
    mavlink_status_t status;
    if (this->parse_mavlink_message(buff, len, msg, status)) {
        this->received_message(msg);
    }
}

size_t MAVLinkConnectionHandler::send_data(const void* buff, size_t len) {
    if (this->tcp_acceptor.connected()) {
        return this->tcp_acceptor.send_data(buff, len);
    } return 0;
}

bool MAVLinkConnectionHandler::received_message(mavlink_message_t m) {
    for (auto h : this->message_handlers) {
        h->handle_mavlink_message(m);
    }
        
}

void MAVLinkConnectionHandler::enqueue_message(const mavlink_message_t m) {
    this->new_message_signal(m);
}

bool MAVLinkConnectionHandler::send_message(const mavlink_message_t& m) {
#define MAX_MAVLINK_MESSAGE_SIZE 300

    uint8_t buf[MAX_MAVLINK_MESSAGE_SIZE];
    u_int16_t len = mavlink_msg_to_send_buffer(buf, &m);
    int bytes_sent = this->tcp_acceptor.send_data(&buf, len);
    if (bytes_sent > 0) ; //fprintf(stdout, "Sent mavlink message (%d bytes)\n", bytes_sent);
    else {
        c->debug_log("Error in sending MAVLink message.\n");
        return false;
    }
    return true;
}

bool MAVLinkConnectionHandler::connection_open() {
    return this->tcp_acceptor.connected();
}

void MAVLinkConnectionHandler::add_message_handler(MAVLinkMessageHandler* h) {
    this->message_handlers.push_back(h);
}