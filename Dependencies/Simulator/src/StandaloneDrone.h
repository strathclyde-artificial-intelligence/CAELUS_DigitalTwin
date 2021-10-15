#ifndef __STANDALONEDRONE_H__
#define __STANDALONEDRONE_H__

#include "Interfaces/DynamicObject.h"
#include "ESCs/SimpleFixedWingESC.h"
#include "Interfaces/DroneController.h"
#include "DroneSensors.h"
#include "DataStructures/LatLonAlt.h"
#include "Containers/DroneConfig.h"
#include "Interfaces/DroneStateProcessor.h"

class StandaloneDrone : public DynamicObject {
protected:
    DroneStateProcessor* drone_state_processor;

    DroneConfig config;
    SimpleFixedWingESC virtual_esc{config};
    DroneController& controller;

// Glasgow LatLon Height
#define INITIAL_LAT 55.8609825
#define INITIAL_LON -4.2488787
#define INITIAL_ALT 2600 // mm

    DroneSensors sensors{(DynamicObject&)*this,
        LatLonAlt{ INITIAL_LAT, INITIAL_LON, INITIAL_ALT }
    };

    void _setup_drone();
    void fake_ground_transform(boost::chrono::microseconds us);
    void mix_controls(boost::chrono::microseconds us);
    
public:
    StandaloneDrone(const char* config_file, Clock& clock, DroneController& controller) :
        DynamicObject(config_from_file_path(config_file), clock),
        config(config_from_file_path(config_file)),
        controller(controller)
        { this->_setup_drone(); };
    
    void set_drone_state_processor(DroneStateProcessor& processor) {
        this->drone_state_processor = &processor;
    }

    void update(boost::chrono::microseconds us) override;
};

#endif // __STANDALONEDRONE_H__