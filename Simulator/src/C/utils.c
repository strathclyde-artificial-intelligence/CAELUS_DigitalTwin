#include "utils.h"

void pp_mavlink_message(mavlink_message_t* msg) {
    printf("<MAVLink: msg ID %d | sequence: %d | component ID %d | system ID %d>\n", msg->msgid, msg->seq, msg->compid, msg->sysid);
}
