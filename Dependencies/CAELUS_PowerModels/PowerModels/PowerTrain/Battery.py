from typing import List, Tuple

from numpy import power
from .batt_disc import batt_disc
from .power_train_esc_motor import powertrain_ESC_Motor
from time import time

class Battery():

    @staticmethod
    def rpm_to_rads(rpm):
        return rpm * 0.10472

    def __init__(self, initial_voltage, initial_modulation_idx, max_motor_rpm, propeller_thrust_factor, motors_n = 4):
        self.__current_modulation_idxs = [initial_modulation_idx]*motors_n
        self.__current_voltage = initial_voltage
        self.__internal_time = 0
        self.__depth_of_discharge = 0
        self.__motors_n = motors_n
        self.__power_train = powertrain_ESC_Motor(max_motor_rpm, propeller_thrust_factor)

    def new_control(self, controls: List[float], dt_hr: float) -> Tuple[float, float]:
        controls = [max(v, 0) for v in controls]

        # HOTFIX FOR FUNCTION THAT HANGS -- MAZHE SHOULD PROVIDE A FIX
        # DELETE WHEN FIXED!!
        controls = [c if c > 0.12 else 0 for c in controls]
        ##
        mod_idxs, capacities_extracted, current_demands = [m for m in self.__current_modulation_idxs], [], []
        for i in range(self.__motors_n):
            c = controls[i]
            if c > 0:
                _, _, new_mod_idx, capacity_extracted, current_demand = self.__power_train(
                        controls[i],
                        self.__current_modulation_idxs[i],
                        self.__current_voltage,
                        dt_hr)
            else:
                new_mod_idx, capacity_extracted, current_demand = mod_idxs[i], 0, 0

            mod_idxs[i] = new_mod_idx
            capacities_extracted.append(capacity_extracted)
            current_demands.append(current_demand)

        new_discharge, new_voltage = batt_disc(self.__depth_of_discharge, sum(capacities_extracted), sum(current_demands))

        self.__current_modulation_idxs = mod_idxs
        self.__current_voltage = new_voltage
        self.__depth_of_discharge = new_discharge

        self.__internal_time += dt_hr

        return self.__current_voltage, self.__depth_of_discharge

    def get_battery_time(self):
        return self.__internal_time

    def get_battery_level(self):
        return max(0, 100 - self.__depth_of_discharge)