#ifndef __TCPCONNECTION_H__
#define __TCPCONNECTION_H__

#pragma GCC diagnostic ignored "-W#pragma-messages"
#pragma GCC diagnostic ignored "-Wdeprecated-declarations"

#include "../Interfaces/DataReceiver.h"
#include <boost/bind.hpp>
#include <boost/shared_ptr.hpp>
#include <boost/enable_shared_from_this.hpp>
#include <boost/asio.hpp>

using namespace boost::asio;

#define MAX_BUFF_LEN 1024

class TCPConnection : public boost::enable_shared_from_this<TCPConnection> {
private:
  ip::tcp::socket _socket;
  char recv_buffer[MAX_BUFF_LEN];
  DataReceiver& data_recv_delegate;
  
  TCPConnection(io_service& service, DataReceiver& recv_delegate) : 
    _socket(service),
    data_recv_delegate(recv_delegate)
  {}

public:
    typedef boost::shared_ptr<TCPConnection> tcp_connection_ptr;
    
    static tcp_connection_ptr create(io_service& service, DataReceiver& recv_delegate) {
        return tcp_connection_ptr(new TCPConnection(service, recv_delegate));
    }

    void start_reading() {
        this->_socket.async_read_some(
          buffer(this->recv_buffer, MAX_BUFF_LEN),
          boost::bind(&TCPConnection::handle_read, 
            shared_from_this(), 
            placeholders::error,
            placeholders::bytes_transferred)
        );
    }

    void handle_read(__attribute__((unused)) const boost::system::error_code& err, size_t bytes_transferred) {
        if (bytes_transferred != 0) this->data_recv_delegate.receive_data((const char*)&this->recv_buffer, bytes_transferred);
        start_reading();
    }
    

    ip::tcp::socket& get_socket() { return _socket; }
}; 

#endif // __TCPCONNECTION_H__