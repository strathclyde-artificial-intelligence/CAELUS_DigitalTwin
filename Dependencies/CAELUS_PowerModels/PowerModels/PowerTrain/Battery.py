from typing import List, Tuple
from .batt_disc import batt_disc
from .power_train_esc_motor import powertrain_ESC_Motor


class Battery():
    def __init__(self, initial_voltage, initial_modulation_idx, timestep_s, motors_n = 4):
        self.__current_modulation_idxs = [initial_modulation_idx]*motors_n
        self.__current_voltage = initial_voltage
        self.__internal_time = 0
        self.__depth_of_discharge = 0
        self.__timestep_s = timestep_s
        self.__motors_n = motors_n

    def new_control(self, controls: List[float]) -> Tuple[float, float]:

        controls = [max(v, 0) for v in controls]
        # HOTFIX FOR FUNCTION THAT HANGS -- MAZHE SHOULD PROVIDE A FIX
        # DELETE WHEN FIXED!!
        controls = [c if c > 0.05 else 0 for c in controls]
        ##
        mod_idxs, capacities_extracted, current_demands = [m for m in self.__current_modulation_idxs], [], []
        for i in range(self.__motors_n):
            motor_pwm = controls[i]
            if motor_pwm == 0:
                continue
            _, _, new_mod_idx, capacity_extracted, current_demand = powertrain_ESC_Motor(
                    controls[i],
                    self.__current_modulation_idxs[i],
                    self.__current_voltage,
                    self.__timestep_s)

            mod_idxs.append(new_mod_idx)
            capacities_extracted.append(capacity_extracted)
            current_demands.append(current_demand)
            

        new_discharge, new_voltage = batt_disc(self.__depth_of_discharge, sum(capacities_extracted), sum(current_demands))

        self.__current_modulation_idxs = mod_idxs
        self.__current_voltage = new_voltage
        self.__depth_of_discharge = new_discharge

        self.__internal_time += self.__timestep_s

        return self.__current_voltage, self.__depth_of_discharge

    def get_battery_time(self):
        return self.__internal_time