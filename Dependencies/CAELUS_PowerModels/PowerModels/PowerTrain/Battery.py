from typing import List, Tuple
from .batt_disc import batt_disc
from .power_train_esc_motor import powertrain_ESC_Motor


class Battery():
    def __init__(self, initial_voltage, initial_modulation_idx, timestep, motors_n = 4):
        self.__current_modulation_idxs = [initial_modulation_idx]*motors_n
        self.__current_voltage = initial_voltage
        self.__internal_time = 0
        self.__depth_of_discharge = 0
        self.__timestep = timestep
        self.__motors_n = motors_n

    def new_control(self, controls: List[float]) -> Tuple[float, float]:
        mod_idxs, capacities_extracted, current_demands = [], [], []
        for i in range(self.__motors_n):
            _, new_mod_idx, capacity_extracted, current_demand, _ = powertrain_ESC_Motor(
                    controls[i],
                    self.__current_modulation_idxs[i],
                    self.__current_voltage,
                    self.__internal_time)

            mod_idxs.append(new_mod_idx)
            capacities_extracted.append(capacity_extracted)
            current_demands.append(current_demand)
            

        new_discharge, new_voltage = batt_disc(self.__depth_of_discharge, sum(capacities_extracted), sum(current_demands))
        
        self.__current_modulation_idxs = mod_idxs
        self.__current_voltage = new_voltage
        self.__depth_of_discharge = new_discharge

        self.__internal_time += self.__timestep

        return self.__current_voltage, self.__depth_of_discharge