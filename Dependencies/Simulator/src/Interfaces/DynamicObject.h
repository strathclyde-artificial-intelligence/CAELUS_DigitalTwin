#ifndef __DYNAMICOBJECT_H__
#define __DYNAMICOBJECT_H__

#include <array>
#include "EnvironmentObject.h"
#include <Eigen/Eigen>

struct DynamicObject : public EnvironmentObject {
public:
    ~DynamicObject() {};
    virtual Eigen::VectorXd& get_state() = 0;
};

#endif // __DYNAMICOBJECT_H__