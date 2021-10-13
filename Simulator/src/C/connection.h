#ifndef __6DOF_CONNECTION__
#define __6DOF_CONNECTION__

#include <sys/socket.h>

typedef struct {
    int sockfd;
    int connfd;
    unsigned int len;
    struct sockaddr_in* simulation_sock;
    struct sockaddr_in* autopilot_sock;
} Connection;

#endif