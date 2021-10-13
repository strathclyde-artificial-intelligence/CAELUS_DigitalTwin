#ifndef __TIMEHANDLER_H__
#define __TIMEHANDLER_H__

#include <boost/chrono.hpp>

class TimeHandler {
public:
    virtual void update(boost::chrono::microseconds us) = 0;
};

#endif // __TIMEHANDLER_H__