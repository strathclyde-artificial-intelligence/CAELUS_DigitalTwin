from threading import current_thread
from ProbeSystem.helper_data.subscriber import Subscriber
from ProbeSystem.helper_data.streams import *
from ThermalModel.ThermalSim import ThermalSim
from ThermalModel.inputs import input_geometry
from ThermalModel.model_atmospheric import model_atmospheric
from ThermalModel.UpdateNodeLink import UpdateNodeLink
from ThermalModel.model_ode import model_ode

class ThermalModelProbe(Subscriber):
    
    def __init__(self, initial_state=None, integrate_every_us = (5 * 60 * 1000000)): # 5 min (5 * 60 * 1000000) integration default
        super().__init__()
        if initial_state is None:
            initial_state = [20, 20, 5, 0, 20]

        self.__time_usec = 0
        self.__integrate_every_us = integrate_every_us
        self.__state = initial_state
        self.__thermal_sim  = ThermalSim(input_geometry(), model_atmospheric, model_ode, UpdateNodeLink)

    def step_state(self, elapsed_time_us):
        dt_s = elapsed_time_us / 1000000
        last_time_s = self.__time_usec / 1000000
        _, solution = self.__thermal_sim.solve(last_time_s, last_time_s+dt_s, self.__state)
        return solution[-1]
    
    def new_datapoint(self, drone_id, stream_id, datapoint):
        elapsed_time_us = (datapoint.time_boot_ms * 1000) - self.__time_usec
        if elapsed_time_us > self.__integrate_every_us:
            new_state = self.step_state(elapsed_time_us)
            self.__state = new_state
            self.__time_usec += elapsed_time_us
        
    # Used by the anra telemetry probe and mission writer -- DO NOT DELETE nor REFACTOR (unless you really know what you are doing)
    def get_payload_temperature(self):
        return self.__state[2]

    def subscribes_to_streams(self):
        return [SYSTEM_TIME]