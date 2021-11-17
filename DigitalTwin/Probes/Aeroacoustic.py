from ProbeSystem.helper_data.subscriber import Subscriber
from ProbeSystem.helper_data.streams import *
from datetime import datetime

class Aeroacoustic(Subscriber):
    
    def __init__(self, write_every=100):
        super().__init__()
        self.lat_lon_alt = None
        self.rotors_speed = None
        self.attitude = None
        self.time_us = None
        self.__last_time = 0
        self.__write_every = write_every
        self.rows = []
        self.__drone_id = None

    def get_rotor_speed(self, datapoint):
        self.rotors_speed = [datapoint.controls[i]*9 if datapoint.controls[i] > 0 else 0 for i in range(4)]
        self.time_us = datapoint.time_usec

    def store_lat_lon_alt(self, datapoint):
        self.lat_lon_alt = [datapoint.lat, datapoint.lon, datapoint.alt]
    
    def store_attitude(self, datapoint):
        self.attitude = [datapoint.roll, datapoint.pitch, datapoint.yaw]

    def store_row(self):
        if self.attitude is not None and self.lat_lon_alt is not None and self.rotors_speed is not None and self.time_us is not None:
            row = [*self.lat_lon_alt, round(self.time_us / 1000000.0, 6)]
            for rs in self.rotors_speed:
                row.extend([rs, *self.attitude])
            self.rows.append(', '.join([str(e) for e in row]))

    def new_datapoint(self, drone_id, stream_id, datapoint):
        if self.__drone_id is None:
            self.__drone_id = drone_id
        if stream_id == HIL_ACTUATOR_CONTROLS:
            if datapoint.time_usec <= self.__last_time:
                return
            self.get_rotor_speed(datapoint)
            self.__last_time = datapoint.time_usec
            self.store_row()
        elif stream_id == GLOBAL_FRAME:
            self.store_lat_lon_alt(datapoint)
        elif stream_id == ATTITUDE:
            self.store_attitude(datapoint)
    
    def save(self):
        t = datetime.utcnow()
        with open(f'aeroacoustic_{self.__drone_id}_{t}.ost', 'w') as f:
            f.write('\n'.join(self.rows))
        
    def subscribes_to_streams(self):
        return [HIL_ACTUATOR_CONTROLS, GLOBAL_FRAME, ATTITUDE]
