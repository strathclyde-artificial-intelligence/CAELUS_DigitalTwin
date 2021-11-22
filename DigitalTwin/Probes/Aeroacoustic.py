from logging import root
from ProbeSystem.helper_data.subscriber import Subscriber
from ProbeSystem.helper_data.streams import *
from datetime import datetime
from bng_latlon import WGS84toOSGB36
from math import e as E

class Aeroacoustic(Subscriber):
    
    def __init__(self):
        super().__init__()
        self.lat_lon_alt = None
        self.rotors_speed = None
        self.attitude = None
        self.time_us = None
        self.__last_time = 0
        self.rows = []
        self.__last_pwms = [0,0,0,0]
        self.__drone_id = None

    def get_rotor_speed(self, datapoint):
        rps = self.pwm_to_rps([c if c > 0 else 0 for c in datapoint.controls][:4])
        self.rotors_speed = [s * 60 for s in rps]
        self.time_us = datapoint.time_usec

    def store_lat_lon_alt(self, datapoint):
        self.lat_lon_alt = [datapoint.lat, datapoint.lon, datapoint.alt]
    
    def store_attitude(self, datapoint):
        self.attitude = [datapoint.roll, datapoint.pitch, datapoint.yaw]

    def pwm_to_rps(self, pwm):
        # FAKE ESC -- Very temporary
        # new_control = [0,0,0,0]
        # sim_timestep = 0.004
        # vtol_kv = 9
        # vtol_tau = 0.006
        # remap = [0, 3, 1, 2]
        # for i in range(len(pwm)):
        #     new_control[i] = self.__last_control[i] + ((sim_timestep * (vtol_kv * pwm[remap[i]] - self.__last_control[i])) / vtol_tau)
        # self.__last_control = new_control
        # print(new_control)
        # return new_control
        
        # THIS IS JMAVSim's ESC
        new_pwms = [0,0,0,0]
        for i in range(len(pwm)):
            new_pwms[i] = self.__last_pwms[i] + (pwm[i] - self.__last_pwms[i]) * (1.0 - E ** (-0.004 / 0.005)) 
        self.__last_pwms = new_pwms
        return [pwm * 9 for pwm in new_pwms]

    def store_row(self):
        if self.attitude is not None and self.lat_lon_alt is not None and self.rotors_speed is not None and self.time_us is not None:
            row = [*self.lat_lon_alt, round(self.time_us / 1000000.0, 6)]
            for rs in self.rotors_speed:
                row.extend([rs, *self.attitude])
            self.rows.append(row)

    def new_datapoint(self, drone_id, stream_id, datapoint):

        if self.__drone_id is None:
            self.__drone_id = drone_id
        if stream_id == HIL_ACTUATOR_CONTROLS:
            if datapoint.time_usec <= self.__last_time:
                return
            self.get_rotor_speed(datapoint)
            self.__last_time = datapoint.time_usec

        elif stream_id == GLOBAL_FRAME:
            self.store_lat_lon_alt(datapoint)
            self.store_row()
        elif stream_id == ATTITUDE:
            self.store_attitude(datapoint)

    
    def convert_lon_lat_to_easting_northing(self, rows):
        def latlon_to_bng(lat, lon):
            return [*WGS84toOSGB36(lat, lon)]

        return [latlon_to_bng(*row[:2]) + row[2:] for row in rows]

    def stringify_rows(self, rows):
        return [', '.join([str(e) for e in row]) for row in rows]

    def save(self):
        t = datetime.utcnow()
        rows = [row for row in self.rows]
        header = f'{len(rows)} {datetime.now().isoformat()}'
        rows = self.convert_lon_lat_to_easting_northing(rows)
        rows = self.stringify_rows(rows)
        rows = [header] + rows
        with open(f'aeroacoustic_{self.__drone_id}_{t}.ost', 'w') as f:
            f.write('\n'.join(rows))
        
    def subscribes_to_streams(self):
        return [HIL_ACTUATOR_CONTROLS, GLOBAL_FRAME, ATTITUDE]
