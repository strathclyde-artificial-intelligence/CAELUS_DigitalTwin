import logging
import os

from DigitalTwin.PayloadModels import SimulatorPayload
from .Interfaces.Stoppable import Stoppable
from .Wrappers.PX4Wrapper import PX4Wrapper
from .Wrappers.SimulatorWrapper import SimulatorWrapper
from .Wrappers.JMAVSimWrapper import JMAVSimWrapper

class SimulationController(Stoppable):
    
    PX4_FOLDER_ENVIRON = 'PX4_ROOT_FOLDER'

    def __init__(self, initial_lon_lat_alt, simulator_payload: SimulatorPayload, stream_handler=None, logger = logging.getLogger(__name__), weather_data_filepath=None):
        self.__simulator_payload = simulator_payload
        self.__logger = logger
        self.__initial_lon_lat_alt = initial_lon_lat_alt
        self.__px4_wrapper = None
        self.__simulator_wrapper = None
        self.__stream_handler = stream_handler
        self.__weather_data_filepath = weather_data_filepath

    def __initialise_all(self):
        if self.__px4_wrapper is None:
            self.__initialise_px4(self.__stream_handler)
        if self.__simulator_wrapper is None:
            self.__initialise_simulator(self.__stream_handler)

    def __initialise_px4(self, stream_handler):
        if SimulationController.PX4_FOLDER_ENVIRON not in os.environ:
            self.__logger.error(f'Environment variable for PX4\'s location not specified. Please export "{SimulationController.PX4_FOLDER_ENVIRON}".')
            exit(-1)
        self.__logger.info('Initialising PX4 instance...')
        self.__px4_wrapper = PX4Wrapper(
            os.environ[SimulationController.PX4_FOLDER_ENVIRON],
            self.__initial_lon_lat_alt,
            self.__simulator_payload.airframe_id,
            stream_handler=stream_handler
        )

    def __initialise_simulator(self, stream_handler):
        self.__logger.info('Initialising simulator instance...')
        # Strathclyde sim workflow
        # self.__simulator_wrapper = SimulatorWrapper(f"{'/'.join(os.path.dirname(__file__).split('/')[:-1])}/Dependencies/Simulator/build/", stream_handler=stream_handler)
        self.__simulator_wrapper = JMAVSimWrapper(
            f'{os.environ[SimulationController.PX4_FOLDER_ENVIRON]}/Tools/jMAVSim/out/production/',
            self.__initial_lon_lat_alt,
            self.__simulator_payload,
            stream_handler=stream_handler,
            weather_data_filepath=self.__weather_data_filepath
        )

    def start(self):
        self.__initialise_all()
        self.__logger.info('Starting PX4Wrapper Thread')
        self.__px4_wrapper.start()
        self.__logger.info('Starting Simulator Thread')
        self.__simulator_wrapper.start()

    def graceful_stop(self):
        self.__px4_wrapper.graceful_stop()
        self.__simulator_wrapper.graceful_stop()

    def halt(self):
        exit(0)

    def reset(self):
        res = True

        self.__logger.info('Waiting for wrappers to free resources...')
        if self.__px4_wrapper is not None:
            self.__px4_wrapper.graceful_stop()
            res = self.__px4_wrapper.termination_complete.acquire(timeout=2)
        if self.__simulator_wrapper is not None:
            self.__simulator_wrapper.graceful_stop()
            res = res and self.__simulator_wrapper.termination_complete.acquire(timeout=2)

        
        # Wait for locks to acquire - if any fail occurs -- halt thread
        if not res:
            self.__logger.warn('Lock acquisition failed -- Halting threads.')
            exit(0)

        self.__px4_wrapper = None
        self.__simulator_wrapper = None

