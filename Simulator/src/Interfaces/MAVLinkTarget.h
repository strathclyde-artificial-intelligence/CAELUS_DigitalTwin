#ifndef __MAVLINKTARGET_H__
#define __MAVLINKTARGET_H__

#include <string>
#include <sock.h>

struct MAVLinkTarget {
    std::string ip_addr;
    std::string port;
    sockaddr_in in_sock;
    sockaddr_in out_sock;
};

#endif // __MAVLINKTARGET_H__