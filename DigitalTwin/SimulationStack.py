import logging
import threading
from PySmartSkies.Models.Operation import Operation
from .SimulationController import SimulationController
from .Interfaces.Stoppable import Stoppable

class SimulationStack(Stoppable):

    def __init__(self, logger = logging.getLogger(__name__)):
        self.__operation_queue: [Operation] = []
        self.__sim_controller = SimulationController()
        self.__logger = logger

    def run_operation(self, operation: Operation):
        self.__logger.info(f'Running operation {operation}.')

    def run_operations(self):
        self.__logger.info('Running all queued operations.')
        for op in self.__operation_queue:
            self.run_operation(op)
        self.__operation_queue = []

    def start(self):
        self.__sim_controller.start()

    def graceful_stop(self):
        self.__sim_controller.graceful_stop()

    def halt(self):
        self.__sim_controller.halt()