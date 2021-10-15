#ifndef __CLOCK_H__
#define __CLOCK_H__

#include <boost/chrono.hpp>
#define DEFAULT_TIMESTEP_SIZE 4000

class Clock {
protected:
    bool time_locked = false;
    boost::chrono::microseconds timestep;
    boost::chrono::microseconds time{0};

public: 
    Clock() : timestep(DEFAULT_TIMESTEP_SIZE) {};
    void unlock_time() { this->time_locked = false; }
    void step(bool lock_time_afterwards = true) { 
        if (this->time_locked) return;
        this->time += this->timestep;
        this->time_locked = lock_time_afterwards ? true : false;
    }
    void set_timestep(boost::chrono::microseconds ts) { this->timestep = ts; }
    boost::chrono::microseconds get_current_time_us() { return this->time; }
};

#endif // __CLOCK_H__