#ifndef __ALIVE_H__
#define __ALIVE_H__

class Alive {
    virtual void set_heartbeat_interval(double interval) = 0;
    virtual double get_heartbeat_interval() = 0;
    virtual void send_heartbeat() = 0;    
    virtual void received_heartbeat() = 0;    
};

#endif // __ALIVE_H__