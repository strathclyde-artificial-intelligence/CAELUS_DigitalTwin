import logging
from .Interfaces.VehicleManager import VehicleManager
from dronekit import connect, Vehicle

class VehicleConnectionManager(VehicleManager):
    def __init__(self, vehicle_manager: VehicleManager = None, vehicle_addr = '127.0.0.1:14540', connection_timeout=10):
        self.__vehicle_addr = vehicle_addr
        self.__vehicle_manager = vehicle_manager
        self.__logger = logging.getLogger(__name__)
        self.__should_connect = False
        self.__connection_timeout = connection_timeout

    def stop_connecting(self):
        self.__should_connect = False

    def set_vehicle_manager(self, vm):
        self.__vehicle_manager = vm

    def connect_to_vehicle(self):
        self.__should_connect = True
        while self.__should_connect:
            try:
                vehicle = connect(self.__vehicle_addr, wait_ready=True, timeout=self.__connection_timeout, heartbeat_timeout=self.__connection_timeout)
                if self.__should_connect:
                    self.vehicle_available(vehicle)
            except Exception as e:
                if self.__should_connect:
                    self.__logger.warn(f'Vehicle connection timeout. Retrying...')
                    self.vehicle_timeout(None)

    def __setup_listeners(self, vehicle: Vehicle):
        pass

    def vehicle_available(self, vehicle):
        self.__setup_listeners(vehicle)
        if self.__vehicle_manager is not None:
            self.__vehicle_manager.vehicle_available(vehicle)
        else:
            self.__logger.warn('Vehicle lock acquired but no Vehicle Manager to broadcast the vehicle to.')

    def vehicle_timeout(self, vehicle):
        self.__logger.warn('Vehicle timed out')
        if self.__vehicle_manager is not None:
            self.__vehicle_manager.vehicle_timeout(vehicle)
        else:
            self.__logger.warn('Vehicle timed out but no Vehicle Manager to broadcast the event to.')
        