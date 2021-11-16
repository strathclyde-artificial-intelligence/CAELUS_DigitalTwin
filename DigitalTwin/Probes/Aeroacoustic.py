from ProbeSystem.helper_data.subscriber import Subscriber
from ProbeSystem.helper_data.streams import *
from time import time

class Aeroacoustic(Subscriber):
    
    def __init__(self):
        super().__init__()
        self.lat_lon_alt = None
        self.rotors_speed = None
        self.attitude = None
        self.time_us = None
        self.rows = []

    def get_rotor_speed(self, datapoint):
        self.rotors_speed = [datapoint.controls[i]*9 if datapoint.controls[i] > 0 else 0 for i in range(4)]
        self.time_us = datapoint.time_usec

    def store_lat_lon_alt(self, datapoint):
        self.lat_lon_alt = [datapoint.lat, datapoint.lon, datapoint.alt]
    
    def store_attitude(self, datapoint):
        self.attitude = [datapoint.roll, datapoint.pitch, datapoint.yaw]

    def store_row(self):
        if self.attitude is not None and self.lat_lon_alt is not None and self.rotors_speed is not None and self.time_us is not None:
            row = [*self.lat_lon_alt, self.time_us / 1000000.0]
            for rs in self.rotors_speed:
                row.extend([rs, *self.attitude])
            self.rows.append(row)

    def new_datapoint(self, drone_id, stream_id, datapoint):
        if stream_id == HIL_ACTUATOR_CONTROLS:
            self.get_rotor_speed(datapoint)
        elif stream_id == GLOBAL_FRAME:
            self.store_lat_lon_alt(datapoint)
        elif stream_id == ATTITUDE:
            self.store_attitude(datapoint)
        self.store_row()
        if len(self.rows) > 0:
            print(f'<>: {self.rows[-1]}')

    def subscribes_to_streams(self):
        return [HIL_ACTUATOR_CONTROLS, GLOBAL_FRAME, ATTITUDE]
