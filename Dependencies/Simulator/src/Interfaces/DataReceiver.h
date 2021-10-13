#ifndef __DATARECEIVER_H__
#define __DATARECEIVER_H__

#include <stdio.h>

class DataReceiver {
public:
    ~DataReceiver() {}
    virtual void receive_data(const char* buff, size_t len) = 0;
};

#endif // __DATARECEIVER_H__