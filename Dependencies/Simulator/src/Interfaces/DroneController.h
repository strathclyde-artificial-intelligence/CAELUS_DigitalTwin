#ifndef __DRONECONTROLLER_H__
#define __DRONECONTROLLER_H__

#include "../Interfaces/AsyncDroneControl.h"
#include "../Interfaces/TimeHandler.h"

class DroneController : public AsyncDroneControl, public TimeHandler {};

#endif // __DRONECONTROLLER_H__