from threading import current_thread
from ProbeSystem.helper_data.subscriber import Subscriber
from ProbeSystem.helper_data.streams import *
from ThermalModel.ThermalSim import ThermalSim
from ThermalModel.inputs import input_geometry
from ThermalModel.model_atmospheric import model_atmospheric
from ThermalModel.UpdateNodeLink import UpdateNodeLink
from ThermalModel.model_ode import model_ode
from Dependencies.CAELUS_ProbeSystem.ProbeSystem.helper_data.streams import MISSION_ITEM_REACHED
import json
import logging
from DigitalTwin.Interfaces.DBAdapter import DBAdapter
from DigitalTwin.WeatherDataProvider import WeatherDataProvider

class TemperatureParser():
    DEFAULT_TEMP = 25.0

    def __init__(self, weather_provider: WeatherDataProvider):
        self.__logger = logging.getLogger()
        self.__temps = []
        self.__prepare_file(weather_provider.get_weather_data_filepath())
        self.__current_wp = 0

    def __prepare_file(self, f_name):
        try:
            with open(f_name, 'r') as f:
                self.__temps = json.loads(f.read())['temperature']
                f.seek(0)
                self.__logger.info("Thermal probe temperature parser OK")
        except Exception as e:
            self.__logger.warn("Error in parsing file for temperature data")
            self.__logger.warn(e)

    def set_current_wp(self, wp):
        if len(self.__temps) == 0:
            return
        if self.__current_wp >= len(self.__temps):
            self.__logger.warn("Requested temperature for out-of-bounds seq. Skipping...")                    
        if wp > self.__current_wp:
            self.__current_wp += 1

    def current_temp(self):
        if len(self.__temps) == 0:
            return TemperatureParser.DEFAULT_TEMP
        temp = self.__temps[self.__current_wp] if self.__current_wp >= 0 else TemperatureParser.DEFAULT_TEMP
        return temp

class ThermalModelProbe(Subscriber):

    def __init__(self, writer: DBAdapter, weather_provider: WeatherDataProvider, initial_state=None, integrate_every_us = (5 * 60 * 1000000)): # 5 min (5 * 60 * 1000000) integration default
        
        super().__init__()
        self.__logger = logging.getLogger()

        self.__latest_seq = 0
        self.__writer = writer
        self.__time_usec = 0
        self.__integrate_every_us = integrate_every_us
        self.__temp_parser = TemperatureParser(weather_provider)
        self.__thermal_sim  = ThermalSim(input_geometry(), lambda _: self.__temp_parser.current_temp(), model_ode, UpdateNodeLink)
        if initial_state is None:
            # 20s need to be the initial state for the package
            wp_0_temp = self.__temp_parser.current_temp()
            initial_state = [wp_0_temp, wp_0_temp, 5, 0, wp_0_temp]      
        self.__state = initial_state

    def step_state(self, elapsed_time_us):
        dt_s = elapsed_time_us / 1000000
        last_time_s = self.__time_usec / 1000000
        try:
            _, solution = self.__thermal_sim.solve(last_time_s, last_time_s+dt_s, self.__state)
            return solution[-1]
        except Exception as e:
            self.__logger.error(f'Thermal model error: {e}')
            return self.__state
        
    
    def new_datapoint(self, drone_id, stream_id, datapoint):
        if stream_id == MISSION_ITEM_REACHED:
            self.__latest_seq = datapoint
            self.__temp_parser.set_current_wp(self.__latest_seq)
        else:
            elapsed_time_us = (datapoint.time_boot_ms * 1000) - self.__time_usec
            if elapsed_time_us > self.__integrate_every_us:
                new_state = self.step_state(elapsed_time_us)
                self.__state = new_state
                self.__time_usec += elapsed_time_us
                self.__writer.store({'payload_temperature': self.__state[2]})
                self.__writer.store({'simulation_time_elapsed': self.__time_usec / 1000000}, series=False)
        
    # Used by the anra telemetry probe and mission writer -- DO NOT DELETE nor REFACTOR (unless you really know what you are doing)
    def get_payload_temperature(self):
        return self.__state[2]

    def get_payload_time(self):
        return self.__time_usec
        
    def subscribes_to_streams(self):
        return [SYSTEM_TIME, MISSION_ITEM_REACHED]