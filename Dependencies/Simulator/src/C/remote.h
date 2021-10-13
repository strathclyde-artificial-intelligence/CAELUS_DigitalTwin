#ifndef __6DOF_REMOTE__
#define __6DOF_REMOTE__

#include <arpa/inet.h>

typedef struct {
    in_addr_t addr;
    uint16_t port;
} Remote;

#endif