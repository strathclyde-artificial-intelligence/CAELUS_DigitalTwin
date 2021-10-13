#ifndef __ENVIRONMENT_H__
#define __ENVIRONMENT_H__

#include <list>
#include "EnvironmentObject.h"
#include "Logger.h"

class Environment : public TimeHandler {
public:
    virtual ~Environment() {}
    Logger* logger;
    std::list<EnvironmentObject*> env_objects;
    virtual void start() = 0;
    virtual void pause() = 0;
    virtual void resume() = 0;
    virtual void add_environment_object(EnvironmentObject& e) = 0;
};

#endif // __ENVIRONMENT_H__