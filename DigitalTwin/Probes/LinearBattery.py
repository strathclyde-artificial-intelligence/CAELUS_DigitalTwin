from typing import List, Tuple
from time import time

class LinearBattery():
    def __init__(self):
        self.__depth_of_discharge = 0

    def new_control(self, controls: List[float], dt_hr: float) -> Tuple[float, float]:
        self.__depth_of_discharge += 0.001
        return 25, self.__depth_of_discharge

    def get_battery_level(self):
        return max(0, 100 - self.__depth_of_discharge)