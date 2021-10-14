import logging
import os
from .Interfaces.Stoppable import Stoppable
from .Wrappers.PX4Wrapper import PX4Wrapper
from .Wrappers.SimulatorWrapper import SimulatorWrapper

class SimulationController(Stoppable):
    
    def __init__(self, stream_handler=None, logger = logging.getLogger(__name__)):
        self.__logger = logger
        self.__px4_wrapper = None
        self.__simulator_wrapper = None
        self.__initialise_px4(stream_handler)
        self.__initialise_simulator(stream_handler)

    def __initialise_px4(self, stream_handler):
        self.__logger.info('Initialising PX4 instance...')
        self.__px4_wrapper = PX4Wrapper('/Users/h3xept/Desktop/PX4-Autopilot', stream_handler=stream_handler)

    def __initialise_simulator(self, stream_handler):
        self.__logger.info('Initialising simulator instance...')
        self.__simulator_wrapper = SimulatorWrapper(f"{'/'.join(os.path.dirname(__file__).split('/')[:-1])}/Dependencies/Simulator/build/", stream_handler=stream_handler)

    def start(self):
        self.__logger.info('Starting PX4Wrapper Thread')
        self.__px4_wrapper.start()
        self.__logger.info('Starting Simulator Thread')
        self.__simulator_wrapper.start()

    def graceful_stop(self):
        self.__px4_wrapper.graceful_stop()
        self.__simulator_wrapper.graceful_stop()

    def halt(self):
        self.__px4_wrapper.halt()
        self.__simulator_wrapper.halt()
    
    def reset(self):
        if self.__px4_wrapper is not None:
            self.__px4_wrapper.graceful_stop()
        if self.__simulator_wrapper is not None:
            self.__simulator_wrapper.graceful_stop()
