import logging
from os import wait
import threading
import time
from typing import List
from PySmartSkies.Models.Operation import Operation
from .Interfaces.Stoppable import Stoppable
from .Interfaces.VehicleManager import VehicleManager
from .SimulationController import SimulationController
from .SimpleDroneCommander import SimpleDroneCommander
from .VehicleConnectionManager import VehicleConnectionManager

class SimulationStack(threading.Thread, Stoppable, VehicleManager):

    def __init__(self, stream_handler = None, logger = logging.getLogger(__name__)):
        super().__init__()
        self.name = 'SimulationStack'
        self.__operation_queue: List[Operation] = []
        self.__sim_controller = SimulationController(stream_handler=stream_handler)
        self.__vehicle_connection_manager = VehicleConnectionManager(self)
        self.__drone_commander = SimpleDroneCommander()
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
        self.__logger.info('Waiting to acquire vehicle lock...')
        self.__vehicle_connection_manager.connect_to_vehicle()

    def run(self):
        self.__start_stack()

    def vehicle_available(self, vehicle):
        self.__drone_commander.set_vehicle(vehicle)
        self.__drone_commander.execute_sample_mission()

    def vehicle_timeout(self, vehicle):
        self.__logger.info('Vehicle timed out. Restarting simulation stack.')
        self.graceful_stop(wait_time=4)
        self.__start_stack()

    def graceful_stop(self, wait_time = 0):
        self.__vehicle_connection_manager.stop_connecting()
        self.__sim_controller.reset()
        if wait_time > 0:
            self.__logger.info(f'Waiting {wait_time} to allow the OS to reallocate resources.')
            time.sleep(wait_time)

    def halt(self):
        self.__sim_controller.halt()
