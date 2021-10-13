#ifndef __ENVIRONMENTOBJECT_H__
#define __ENVIRONMENTOBJECT_H__

#include "TimeHandler.h"
#include "PrettyPrintable.h"

class EnvironmentObject : public TimeHandler, public PrettyPrintable {
public: 
    virtual ~EnvironmentObject() {}
};

#endif // __ENVIRONMENTOBJECT_H__