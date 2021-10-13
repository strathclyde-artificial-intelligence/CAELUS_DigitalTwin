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
    def __init__(self, state_aggregator, should_shutdown):
        self.state_aggregator = state_aggregator
        self.system = None
        self.__initialised = False
        self.should_shutdown = should_shutdown

    def initialise(self, is_done_lock):
        try:
            print(f'Initialising bridge...')
            self.system = kit.connect('127.0.0.1:14540', wait_ready=True)
        except Exception as e:
            print('Failed in initialising SimulationBridge')
            raise e
        self.__initialised = True
        is_done_lock.acquire()
        is_done_lock.notify()
        is_done_lock.release()
        self.setup_telemetry_listeners()

    def is_initialised(self):
        return self.__initialised

    def get_available_streams(self):
        return [var for var in dir(streams) if not var.startswith("__")]

    def new_datapoint(self, vehicle, name, val):
        self.state_aggregator.new_datapoint_for_stream(name, val)

    def setup_telemetry_listeners(self):
        self.system.add_attribute_listener('*', lambda _self,name, val: self.new_datapoint(_self, name, val))