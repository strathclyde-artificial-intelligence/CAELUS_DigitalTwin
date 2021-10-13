#ifndef __AERODYNAMICS_EXTENSION_H__
#define __AERODYNAMICS_EXTENSION_H__

#include "../ForceModels/Aerodynamics.h"
#include "../Containers/DroneConfig.h"

class Aerodynamics : public caelus_fdm::Aerodynamics {
public:
    Aerodynamics(DroneConfig conf) : caelus_fdm::Aerodynamics(
        conf.c,
        conf.thruster_klift,
        conf.S,
        conf.drone_aero_config,
        NULL
    ) {};
};

#endif // __AERODYNAMICS_EXTENSION_H__