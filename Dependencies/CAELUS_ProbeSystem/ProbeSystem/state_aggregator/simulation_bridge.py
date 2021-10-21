from time import sleep
import asyncio
import time 
import threading 
import concurrent
import inspect
import dronekit as kit
from ..helper_data import streams
from threading import Condition

class SimulationBridge():
    def __init__(self, state_aggregator, should_shutdown, should_manage_vehicle = True):
        self.state_aggregator = state_aggregator
        self.system = None
        self.__initialised = False
        self.should_shutdown = should_shutdown
        self.__should_manage_vehicle = should_manage_vehicle
    
    def vehicle_acquired(self, is_done_lock, vehicle):
        self.system = vehicle
        self.__initialised = True
        if is_done_lock is not None:
            is_done_lock.acquire()
            is_done_lock.notify()
            is_done_lock.release()
        self.setup_telemetry_listeners()

    def initialise(self, is_done_lock):
        if self.__should_manage_vehicle:
            try:
                print(f'Initialising bridge...')
                vehicle = kit.connect('127.0.0.1:14540', wait_ready=True)
                self.vehicle_acquired(is_done_lock, vehicle)
            except Exception as e:
                print('Failed in initialising SimulationBridge')
                raise e
        self.vehicle_acquired(is_done_lock, self.system)

    def is_initialised(self):
        return self.__initialised

    def get_available_streams(self):
        return [getattr(streams, var) for var in dir(streams) if not var.startswith("__")]

    def new_datapoint(self, vehicle, name, val):
        self.state_aggregator.new_datapoint_for_stream(name, val)

    def setup_telemetry_listeners(self):
        self.system.add_attribute_listener('*', lambda _self,name, val: self.new_datapoint(_self, name, val))