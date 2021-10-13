#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#include <mavlink.h>

#include "communication.h"
#include "error_messages.h"
#include "sock.h"
#include "utils.h"

bool establish_outbound_tcp_connection(Remote r, Connection* c) {
    c->sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (c->sockfd == -1) goto fatal_sock_creation;
    
    c->simulation_sock = calloc(1, sizeof(struct sockaddr_in));
    bzero(c->simulation_sock, sizeof(*c->simulation_sock));
    c->simulation_sock->sin_family = AF_INET;
    c->simulation_sock->sin_addr.s_addr = r.addr;
    c->simulation_sock->sin_port = r.port;

    int connection_res = connect(c->sockfd, (const struct sockaddr *) c->simulation_sock, sizeof(c->simulation_sock));
    if (connection_res == 0)
        printf("Connection enstabilished %d\n", c->sockfd);
    else goto fatal_sock_connection;
    return true;

fatal_sock_creation:
    fprintf(stderr, SOCK_CREATION_ERROR_MSG);
    return false;
fatal_sock_connection:
    fprintf(stderr, SOCK_CONNECTION_ERROR_MSG);
    return false;
}

bool sock_listen(Connection* c) {
    int listen_res = listen(c->sockfd, 5);
    if (listen_res == 0) fprintf(stdout, "Listening on port %d\n", c->simulation_sock->sin_port);
    return true;

fatal_sock_listen:
    fprintf(stderr, SOCK_LISTENING_ERROR_MSG);
    return false;
}

bool sock_accept(Connection* c) {
    c->connfd = accept(c->sockfd, (struct sockaddr*) c->autopilot_sock, &c->len);
    if (c->connfd >= 0) fprintf(stdout, "Sockfd %d accepted remote connection\n", c->sockfd);
    return true;

fatal_accept:
    fprintf(stderr, SOCK_ACCEPT_ERROR_MSG);
    return false;
}

bool accept_inbound_tcp_connection(uint32_t port, Connection* c) {
    c->sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (c->sockfd == -1) goto fatal_sock_creation;
    
    bzero(c->simulation_sock, sizeof(*c->simulation_sock));
    c->simulation_sock->sin_family = AF_INET;
    c->simulation_sock->sin_addr.s_addr = htonl(INADDR_ANY);
    c->simulation_sock->sin_port = port;

    int bind_res = bind(c->sockfd, (const struct sockaddr *) c->simulation_sock, sizeof(*c->simulation_sock));
    if (bind_res == 0) fprintf(stdout, "Sock binding successful (%d)\n", port);
    else goto fatal_sock_binding;
    c->len = sizeof(c->autopilot_sock);

    sock_listen(c);
    sock_accept(c);

    return true;
    
fatal_sock_creation:
    fprintf(stderr, SOCK_CREATION_ERROR_MSG);
    exit(-1);
fatal_sock_binding:
    fprintf(stderr, SOCK_BIND_ERROR_MSG);
    fprintf(stderr, "Errno: %d (%s)\n", errno, strerror(errno));
    exit(-1);  
}

int main(int argc, char const *argv[])
{
    Remote r; 
    r.addr = inet_addr("127.0.0.1");
    r.port = htons(4560);

    Connection* c = calloc(1, sizeof(Connection));
    c->simulation_sock = calloc(1, sizeof(struct sockaddr_in));
    c->autopilot_sock = calloc(1, sizeof(struct sockaddr_in));
    accept_inbound_tcp_connection(htons(4560), c);

    mavlink_message_t* msg = calloc(1, sizeof(mavlink_message_t));
    uint16_t len = m_px4_heartbeat(c, msg);
    uint8_t buf[2048] = {0};
    
    handle_messages(c);

    return 0;
}

