from logging import root
from ProbeSystem.helper_data.subscriber import Subscriber
from ProbeSystem.helper_data.streams import *
from datetime import datetime
from bng_latlon import WGS84toOSGB36
from math import e as E
from queue import Empty, Queue
import numpy as np
from DigitalTwin.Interfaces.DBAdapter import DBAdapter
from DigitalTwin.Vehicle import Vehicle

class Aeroacoustic(Subscriber):
    ROTOR_N = 5
    def __init__(self, writer: DBAdapter):
        super().__init__()
        self.lat_lon_alt = None
        self.rotors_speed = None
        self.attitude = None
        self.time_us = None
        self.__last_time = 0
        self.rows = []
        self.__last_pwms = [0] * Aeroacoustic.ROTOR_N
        self.__drone_id = None
        self.__vehicle = None
        self.__mission_status_queue = Queue()
        self.__agl_altitude = None
        self.__home_elevation = None
        self.__writer: DBAdapter = writer
        self.__cruise_sample_step = 0
        self.__cruise_sample_throttle = 15 # Save every x

    @staticmethod
    def euler_to_rotm(yaw, pitch, roll):
        Rz_yaw = np.array([
            [np.cos(yaw), -np.sin(yaw), 0],
            [np.sin(yaw),  np.cos(yaw), 0],
            [          0,            0, 1]])
        Ry_pitch = np.array([
            [ np.cos(pitch), 0, np.sin(pitch)],
            [             0, 1,             0],
            [-np.sin(pitch), 0, np.cos(pitch)]])
        Rx_roll = np.array([
            [1,            0,             0],
            [0, np.cos(roll), -np.sin(roll)],
            [0, np.sin(roll),  np.cos(roll)]])

        return np.dot(Rz_yaw, np.dot(Ry_pitch, Rx_roll))

    def get_direction_vector_from_rpy(self, initial_vec, r, p, y):
        return np.array(initial_vec).dot(Aeroacoustic.euler_to_rotm(y, p, r))

    def get_rotor_speed(self, datapoint):
        rps = self.pwm_to_rps([c if c > 0 else 0 for c in datapoint.controls][:5])
        self.rotors_speed = [s * 60 for s in rps]
        self.time_us = datapoint.time_usec

    def store_lat_lon_alt(self, datapoint):
        alt = (datapoint.alt - self.__home_elevation) if self.__home_elevation is not None else 0
        if self.__agl_altitude is not None:
            alt = max(0, min(alt, self.__agl_altitude))
        self.lat_lon_alt = [datapoint.lat, datapoint.lon, alt]

    def store_attitude(self, datapoint):
        self.attitude = self.get_direction_vector_from_rpy([0,0,1], datapoint.roll, datapoint.pitch, datapoint.yaw)
        self.pusher_attitude = self.get_direction_vector_from_rpy([-1,0,0], datapoint.roll, datapoint.pitch, datapoint.yaw)

    def set_vehicle(self, v):
        self.__vehicle = v

    def pwm_to_rps(self, pwm):
        # THIS IS JMAVSim's ESC
        new_pwms = [0] * Aeroacoustic.ROTOR_N
        for i in range(len(pwm)):
            new_pwms[i] = self.__last_pwms[i] + (pwm[i] - self.__last_pwms[i]) * (1.0 - E ** (-0.004 / 0.005)) 
        self.__last_pwms = new_pwms
        return [pwm * 9 for pwm in new_pwms]

    def store_row(self):
        if self.attitude is not None and self.lat_lon_alt is not None and self.rotors_speed is not None and self.time_us is not None:
            self.__process_mission_status()
            should_store = self.__cruise_sample_step % self.__cruise_sample_throttle == 0
            self.__cruise_sample_step += 1
            if not should_store:
                return
            row = [*self.lat_lon_alt, round(self.time_us / 1000000.0, 6)]
            for rs, att in zip(self.rotors_speed, [self.attitude]*4 + [self.pusher_attitude]):
                row.extend([rs, *att])
            self.__writer.store({'aeroacoustic': row})

    def __process_mission_status(self):
        try:
            new_status = self.__mission_status_queue.get_nowait()
            self.__mission_status = new_status
            if new_status == Vehicle.TAKING_OFF:
                self.__home_elevation = self.__vehicle.home_location.alt
            if new_status == Vehicle.TAKEOFF_COMPLETE:
                # ASSUMES CONSTANT AGL ALTITUDE AFTER TAKEOFF
                self.__agl_altitude = self.lat_lon_alt[2]
        except Empty as _:
            pass

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
        t_h = datetime.now().isoformat().split(".")[0]+'Z'
        header = f'{len(rows)} {t_h}'
        rows = self.convert_lon_lat_to_easting_northing(rows)
        rows = self.stringify_rows(rows)
        rows = [header] + rows
        with open(f'aeroacoustic_{self.__drone_id}_{t}.ost', 'w') as f:
            f.write('\n'.join(rows))
        
    def subscribes_to_streams(self):
        return [HIL_ACTUATOR_CONTROLS, GLOBAL_FRAME, ATTITUDE]
