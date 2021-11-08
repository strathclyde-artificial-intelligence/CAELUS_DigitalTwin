from typing import Tuple, List
import logging
from os import wait
import threading
import time
from typing import List
from queue import Queue
from PySmartSkies.Models.Operation import Operation
from .Interfaces.Stoppable import Stoppable
from .Interfaces.VehicleManager import VehicleManager
from .Interfaces.MissionManager import MissionManager
from .Interfaces.SimulationStack import SimulationStack
from .SimulationController import SimulationController
from .PayloadModels import SimulatorPayload

class CAELUSSimulationStack(threading.Thread, SimulationStack, Stoppable, VehicleManager, MissionManager):

    def __init__(self, drone_config: SimulatorPayload, stream_handler = None, logger = logging.getLogger(__name__)):
        super().__init__()
        self.name = 'CAELUSSimulationStack'
        self.__operation_queue: List[Operation] = []
        self.__sim_controller = SimulationController(drone_config.initial_lon_lat_alt, stream_handler=stream_handler)
        # Thread safe queue of ([Waypoint], altitude)
        self.__mission_queue = Queue()
        self.__logger = logger

    def run_operation(self, operation: Operation):
        self.__logger.info(f'Running operation {operation}.')

    def run_operations(self):
        self.__logger.info('Running all queued operations.')
        for op in self.__operation_queue:
            self.run_operation(op)
        self.__operation_queue = []

    def __start_stack(self):
        self.__sim_controller.start()

    def run(self):
        self.__start_stack()

    def vehicle_available(self, vehicle):
        self.__drone_commander.set_vehicle(vehicle)

    def vehicle_timeout(self, vehicle):
        self.__logger.info('Vehicle timed out')

    def graceful_stop(self, wait_time = 0):
        self.__sim_controller.reset()
        if wait_time > 0:
            self.__logger.info(f'Waiting {wait_time} to allow the OS to reallocate resources.')
            time.sleep(wait_time)

    def halt(self):
        self.__sim_controller.halt()

    def add_mission(self, mission: Tuple[List[float], float]):
        self.__mission_queue.put(mission)

    def restart_stack(self):
        self.graceful_stop(wait_time=4)
        self.__start_stack()
