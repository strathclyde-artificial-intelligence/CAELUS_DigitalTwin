#include <stdbool.h>
#include <errno.h>
#include <mavlink.h>

#include "error_messages.h"
#include "communication.h"

bool m_px4_heartbeat(Connection* c, mavlink_message_t* msg) {
    mavlink_msg_heartbeat_pack(1, 200, msg, MAV_TYPE_HELICOPTER, MAV_AUTOPILOT_GENERIC, MAV_MODE_GUIDED_ARMED, 0, MAV_STATE_ACTIVE);
    return true;
}

bool m_set_msg_interval(Connection* c, mavlink_message_t* msg) {
    mavlink_msg_message_interval_pack(1, 200, msg, MAV_CMD_SET_MESSAGE_INTERVAL, 1);
    return true;
}

bool m_px4_status(Connection* c, mavlink_message_t* msg) {
    mavlink_msg_sys_status_pack(1, 200, msg, 0, 0, 0, 500, 11000, -1, -1, 0, 0, 0, 0, 0, 0);
    return true;
}

bool send_mavlink_msg(Connection* c, mavlink_message_t* msg, u_int8_t* buf) {
    u_int16_t len = mavlink_msg_to_send_buffer(buf, msg);
    int bytes_sent = sendto(c->connfd, buf, len, 0, (struct sockaddr*) c->autopilot_sock, sizeof(struct sockaddr*));
    
    if (bytes_sent > 0) fprintf(stdout, "Sent mavlink message (%d bytes)\n", bytes_sent);
    else goto fatal_send;
    return true;

fatal_send:
    fprintf(stderr, MAVLINK_MSG_SEND_ERROR);
    fprintf(stderr, "Errno: %d (%s)\n", errno, strerror(errno));
}

ssize_t receive_message(Connection* c, uint8_t* buff, size_t maxlen) {
    int8_t buffer[2048] = {0};
    ssize_t len = 0;
    if ((len = recv(c->connfd, buff, maxlen, 0) == -1))
        goto error;

    return len;
error:
    fprintf(stderr, SOCK_READ_ERROR_MSG);
    fprintf(stderr, "Errno: %d (%s).\n", errno, strerror(errno));
}

void handle_messages(Connection* c) {
    mavlink_message_t msg;
    mavlink_status_t status;
    uint8_t buf[300] = {0};
    mavlink_command_long_t pre_flight_msg;

    while(true) {
        ssize_t len = recv(c->connfd, &buf, sizeof(buf), 0x0);
        printf("Reading %zd bytes\n", len);
        for (int i = 0; i < len; i++) {
            if (mavlink_parse_char(MAVLINK_COMM_0, buf[i], &msg, &status)) {
                switch(msg.msgid) {
                    case MAVLINK_MSG_ID_HEARTBEAT:
                        printf("HB!\n");
                        break;
                    case MAVLINK_MSG_ID_COMMAND_LONG:
                        mavlink_msg_command_long_decode(&msg, &pre_flight_msg);
                        fprintf(stdout, "Pre-flight calibration request (command_id: %d).\n", pre_flight_msg.command);
                        switch(pre_flight_msg.command) {
                            case MAV_CMD_SET_MESSAGE_INTERVAL:
                                m_set_msg_interval(c, &msg);
                                send_mavlink_msg(c, &msg, buf);
                                break;
                            default:
                                fprintf(stdout, "Unknown command %d\n", pre_flight_msg.command);
                        }
                        break;
                    default:
                        printf("Some message with ID %d\n", msg.msgid);
                }
            }
        }
    }
}

void send_heartbeat(Connection* c) {
    mavlink_message_t hb;
    uint8_t buff[256] = {0};
    m_px4_heartbeat(c, &hb);
    send_mavlink_msg(c, &hb, &buff);
}