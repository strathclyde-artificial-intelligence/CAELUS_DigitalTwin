#ifndef __LOGGER_H__
#define __LOGGER_H__

#include <string>

#define ERROR_PREFIX "[ERROR] "

class Logger {
public:
    virtual ~Logger() {}
    virtual void log(std::string s) = 0;
    virtual void set_debug(bool debug) = 0;
    virtual bool debug_mode_active() = 0;
    void err_log(std::string s) { this->log(std::string{ERROR_PREFIX}.append(s)); };
    void debug_log(std::string s) { if (this->debug_mode_active()) this->log(s); }
};

#endif // __LOGGER_H__