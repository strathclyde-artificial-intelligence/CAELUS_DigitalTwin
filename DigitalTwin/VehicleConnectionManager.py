from threading import Thread, Condition
import logging
from .Interfaces.VehicleManager import VehicleManager
from .Vehicle import Vehicle
from dronekit import connect

class VehicleConnectionManager(VehicleManager):
    def __init__(self, vehicle_manager: VehicleManager = None, vehicle_addr = '127.0.0.1:14550', connection_timeout=20):
        print(self)
        self.__vehicle_addr = vehicle_addr
        self.__vehicle_manager = vehicle_manager
        self.__vehicle = None
        self.__logger = logging.getLogger(__name__)
        self.__should_connect = False
        self.__connection_timeout = connection_timeout

    def stop_connecting(self):
        self.__should_connect = False
        if self.__vehicle is not None:
            self.__vehicle.close()

    def set_vehicle_manager(self, vm):
        self.__vehicle_manager = vm

    def __connect_to_vehicle(self):
        try:
            vehicle = connect(self.__vehicle_addr, wait_ready=True, timeout=self.__connection_timeout, heartbeat_timeout=self.__connection_timeout, vehicle_class=Vehicle, source_system=1)
            self.__vehicle = vehicle
        except Exception as e:
            if self.__should_connect:
                self.__logger.warn(e)
                self.__logger.warn(f'Vehicle connection timeout. Retrying...')
        finally:
            if self.__should_connect:
                if self.__vehicle is not None:
                    self.vehicle_available(self.__vehicle)
                else:
                    self.vehicle_timeout(self.__vehicle)

    def connect_to_vehicle(self):
        self.__logger.info('Starting vehicle connection')
        self.__should_connect = True
        t = Thread(target=self.__connect_to_vehicle)
        t.name = 'Vehicle Connection'
        t.daemon = True
        t.start()
        
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
        