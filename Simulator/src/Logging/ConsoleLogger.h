#ifndef __CONSOLELOGGER_H__
#define __CONSOLELOGGER_H__

#include <string>
#include <mutex>
#include "../Interfaces/Logger.h"

enum LoggerMode { NORMAL, DEBUG };

class ConsoleLogger : public Logger {
private:
    static ConsoleLogger* instance;
    static std::mutex mutex;
    LoggerMode log_mode;
protected:
    ConsoleLogger() {};
    ~ConsoleLogger() {};
public:
    static ConsoleLogger* shared_instance();
    ConsoleLogger(ConsoleLogger&c) = delete;
    void log(std::string s) override;
    void set_debug(bool debug) override;
    bool debug_mode_active() override;
};

#endif // __CONSOLELOGGER_H__