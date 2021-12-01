from ProbeSystem.helper_data.subscriber import Subscriber
from ProbeSystem.helper_data.streams import *
from PowerModels.PowerTrain.Battery import Battery
from .LinearBattery import LinearBattery
from ..Vehicle import Vehicle
from time import time
from ..Interfaces.DBAdapter import DBAdapter

US_TO_HR = 1 / 3.6e9

class QuadrotorBatteryDischarge(Subscriber):
    
    def __init__(self, writer: DBAdapter):
        super().__init__()
        # REMOVED until MAZE will fix the model
        self.__battery = Battery(25.2, 0.0)
        # self.__battery = LinearBattery()
        self.__vehicle = None
        self.__last_timestamp = 0
        self.__writer: DBAdapter = writer

    def set_vehicle(self, vehicle):
        self.__vehicle: Vehicle = vehicle

    def new_datapoint(self, drone_id, stream_id, datapoint):
        
        if self.__vehicle is None:
            return
        if self.__battery.get_battery_level() == 0:
            return
        
        # UORb messages are not guaranteed to arrive once per timestep - we must interpolate integration steps
        ts = datapoint.time_usec 
        dt = ts - self.__last_timestamp
        self.__last_timestamp = ts

        curr_voltage, depth_of_discharge = self.__battery.new_control(datapoint.controls, dt * US_TO_HR)
        battery_level = int(100 - depth_of_discharge)

        self.__vehicle.message_factory.battery_status_send(
            0, # batt-id
            1, # battery function https://mavlink.io/en/messages/common.html#MAV_BATTERY_FUNCTION
            3, # battery type https://mavlink.io/en/messages/common.html#MAV_BATTERY_TYPE
            25, # temperature deg
            [int(curr_voltage*1000), *[0xffff]*9], # voltages array (batt is 1 cell so only first one is filled. 0xffff is UINT16_MAX and represents an invalid value)
            -1, # current battery
            -1, # current consumed
            -1, # energy consumed
            int(battery_level), # battery remaining
        )

        self.__writer.store({'battery_level': battery_level})

    def subscribes_to_streams(self):
        return [HIL_ACTUATOR_CONTROLS]

    def get_battery(self):
        return self.__battery