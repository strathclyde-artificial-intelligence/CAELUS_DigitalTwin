from ProbeSystem.helper_data.subscriber import Subscriber
from ProbeSystem.helper_data.streams import *
from PowerModels.PowerTrain.Battery import Battery
from ..Vehicle import Vehicle
from time import time

class QuadrotorBatteryDischarge(Subscriber):
    
    def __init__(self, integration_timestep=1.11111e-6):
        self.__battery = Battery(25.2, 0.0, integration_timestep)
        self.__vehicle = None

    def set_vehicle(self, vehicle):
        self.__vehicle: Vehicle = vehicle

    def new_datapoint(self, drone_id, stream_id, datapoint):
        if self.__vehicle is None:
            return
        if self.__battery.get_battery_level() == 0:
            return
        curr_voltage, depth_of_discharge = self.__battery.new_control(datapoint.controls)
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