from ProbeSystem.helper_data.subscriber import Subscriber
from ProbeSystem.helper_data.streams import *
from PowerModels.PowerTrain.Battery import Battery
from ..Vehicle import Vehicle
from time import time

US_TO_HR = 1 / 3.6e9

class QuadrotorBatteryDischarge(Subscriber):
    
    def __init__(self):
        self.__battery = Battery(25.2, 0.0)
        self.__vehicle = None
        self.__last_timestamp = 0

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
        self.__vehicle.message_factory.battery_status_send(
            0, # batt-id
            1, # battery function https://mavlink.io/en/messages/common.html#MAV_BATTERY_FUNCTION
            3, # battery type https://mavlink.io/en/messages/common.html#MAV_BATTERY_TYPE
            25, # temperature deg
            [int(curr_voltage*1000), *[0xffff]*9], # voltages array (batt is 1 cell so only first one is filled. 0xffff is UINT16_MAX and represents an invalid value)
            -1, # current battery
            -1, # current consumed
            -1, # energy consumed
            int(self.__battery.get_battery_level()), # battery remaining
        )

    def subscribes_to_streams(self):
        return [HIL_ACTUATOR_CONTROLS]