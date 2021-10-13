#ifndef __TCPACCEPTOR_H__
#define __TCPACCEPTOR_H__

#include <stdio.h>
#include <boost/asio.hpp>
#include "TCPConnection.h"
#include "../Interfaces/DataSender.h"
#include "../Interfaces/DataReceiver.h"


class TCPAcceptor : public DataReceiver, public DataSender {
private:
    boost::asio::ip::tcp::acceptor _acceptor;
    boost::asio::io_service& service;
    std::vector<DataReceiver*> broadcast_recv;
    TCPConnection::tcp_connection_ptr connection = NULL;
    void handle_accept(TCPConnection::tcp_connection_ptr conn, const boost::system::error_code& err);
public:
    TCPAcceptor(boost::asio::io_service& service, int port);
    ~TCPAcceptor();
    void start();
    void add_data_receiver(DataReceiver* r);
    bool connected();
    void receive_data(const char* buff, size_t len) override;
    size_t send_data(const void* buff, size_t len) override;
};

#endif // __TCPACCEPTOR_H__