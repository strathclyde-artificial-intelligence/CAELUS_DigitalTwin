#ifndef __6DOF_COMMUNICATION__
#define __6DOF_COMMUNICATION__

#include <stdbool.h>
#include "connection.h"

bool m_px4_heartbeat(Connection* c, mavlink_message_t* msg);
bool m_px4_status(Connection* c, mavlink_message_t* msg);
bool m_set_msg_interval(Connection* c, mavlink_message_t* msg);

void send_heartbeat(Connection* c);

bool send_mavlink_msg(Connection* c, mavlink_message_t* msg, u_int8_t* buf);
void handle_messages(Connection* c);
ssize_t receive_message(Connection* c, uint8_t* buff, size_t maxlen);

#endif