#ifndef __6DOFSIM_SOCK__
#define __6DOFSIM_SOCK__

#include <stdbool.h>
#include "remote.h"
#include "connection.h"

bool enstabilish_tcp_connection(Remote r, Connection* c);
bool accept_inbound_tcp_connection(uint32_t port, Connection* c);

#endif