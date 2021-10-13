# CAELUS PowerModels
[![PyPowerModels Test](https://github.com/strathclyde-artificial-intelligence/CAELUS_PowerModels/actions/workflows/python-app.yml/badge.svg)](https://github.com/strathclyde-artificial-intelligence/CAELUS_PowerModels/actions/workflows/python-app.yml)

A python port of the power models developed by Ikenn Efika for the CAELUS project (Strathclyde University).

# Exposed functions

### Powertrain ESC Motor
This function is designed to represent the Electronic speed controller and motor for each motor on the Avy Aera Drone. 

This function is specific to the Avy Aera drone as it uses the motor parameters and constants provided by Avy for their drone.

#### powertrain_ESC_Motor(w_ref, m_init, v_batt, dT)
#### Parameters:
*w_ref*:
Motor Speed reference (-1 to 1) provided from Px4 to the ESC

*m_init*:
The last state of Modulation Index from a database

*v_batt*:
The Source (Battery) voltage, provided by a battery discharge function in a feedback loop (or database)

*dT*:
Sample time of the model: in hours (i.e. 1 sec =  1/3600)

#### Returns:
A list containing the following data:

*w*:
The motor speed value provided from Px4 to an ESC

*thrust*:
The thrust produced under current conditions

*mod*:
The current state of Modulation Index to store in a database

*Qcon*:
Energy Capacity (Ah) consumed, to be sent to battery model

*Idis*:
The current demand from the system


#### Assumptions
* tau_electrical << tau_mechanical << tau_aerodynamics

* Response to a step change in speed is <= 100ms

* w_ref: 1 = Max motor speed clockwise -1 = Max motor speed anticlockwise

* All motors (including cruise motor) are identical

### Battery discharge
#### batt_disc(depth_of_discharge, capacity, current)
#### Parameters:

*depth_of_discharge*:
An integer value in the range 0-100 representing the current depth of discharge of the battery.

*capacity*:
The energy extracted from the battery in [Ah]

*current*:
Current flowing out of the battery (LPF filtered) [A]

#### Returns:
A list in the format `[depth_of_discharge, v_batt]`

### Demand schedule
`NOTE: Post-processing method`

#### demand_schedule(landings, base_load)
#### Parameters: 

*landings*:
A list of landing datapoints.
Each datapoint is in the format:
`[[YYYY MM dd hh mm ss], depth_of_discharge, c_rate]`

*base_load*: ? (default 0)

#### Returns:
? (Description of return value)

### Charge CCCV
#### charge_cccv(depth_of_discharge, c_rate)
#### Parameters:
*depth_of_discharge*:
An integer value in the range 0-100 representing the current depth of discharge of the battery.

*c_rate*:
The C rating of the battery.

#### Returns:
The time to fully charge the battery. 
