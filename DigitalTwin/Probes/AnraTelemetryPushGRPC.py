from ProbeSystem.helper_data.subscriber import Subscriber
from ProbeSystem.helper_data.streams import *
from dataclasses import dataclass, asdict
from typing import List
import time
from ..gRPC import Telemetry_pb2_grpc, Telemetry_pb2
import grpc
from math import pi
import logging

M_TO_KNOT = 1.944
M_TO_FOOT = 3.281
RAD_TO_DEG = 180 / pi
class AnraTelemetryPushGRPC(Subscriber):

    def __init__(self):
        super().__init__()

        self.data = {
            'roll': 0,
            'pitch': 0,
            'yaw': 0,
            'gps_0': None,
            'velocity': [0,0,0],
            'global_frame':None,
            'heading': 0,
            'ground_speed':0
        }

        self.__remote_ip = 'localhost'
        self.__remote_port = 4200
        self.__channel = grpc.insecure_channel(f'{self.__remote_ip}:{self.__remote_port}')
        self.__grpc_stub = Telemetry_pb2_grpc.TelemetryModuleStub(self.__channel)
        self.__initialised = False
        self.__sim_time = None
        self.__logger = logging.getLogger()

    def set_mission_details(self,
        drone_registration,
        operation_id,
        control_area_id,
        reference_number,
        dis_token):

        self.__initialised = True
        self.drone_registration = drone_registration
        self.operation_id = operation_id
        self.control_aread_id = control_area_id
        self.reference_number = reference_number
        self.dis_token = dis_token

    def get_hdop(self):
        if self.data['gps_0'] is None:
            return 100        
        return self.data['gps_0'].eph

    def get_vdop(self):
        if self.data['gps_0'] is None:
            return 100
        return self.data['gps_0'].epv

    def get_sat_number(self):
        if self.data['gps_0'] is None:
            return 0
        return self.data['gps_0'].satellites_visible
        
    def get_climbrate(self):
        return self.data['velocity'][-1] # z vel

    def pack_altitude(self):
        if self.data['global_frame'] is None:
            return 0
        return self.data['global_frame'].alt


    def get_timestamp(self):
        return self.__sim_time

    def pack_telemetry(self):
        telemetry = Telemetry_pb2.Telemetry()

        telemetry.operation_id = self.operation_id
        telemetry.enroute_positions_id = '??'
        telemetry.registration_id = self.drone_registration
        telemetry.reference_number = self.reference_number

        telemetry.location.type = 'Point'
        telemetry.location.lat = self.data['global_frame'].lat if self.data['global_frame'] is not None else 0
        telemetry.location.lng = self.data['global_frame'].lon if self.data['global_frame'] is not None else 0

        telemetry.ground_speed_kt = self.data['ground_speed'] * M_TO_KNOT
        telemetry.time_send = self.get_timestamp()
        telemetry.battery_remaining = self.data['battery_level']
        telemetry.mode = 'quadrotor'
        telemetry.altitude_ft_wgs84 = self.pack_altitude() * M_TO_FOOT
        telemetry.altitude_num_gps_satellites = self.get_sat_number()
        telemetry.hdop_gps = self.get_hdop()
        telemetry.track_bearing_deg = self.data['yaw'] * RAD_TO_DEG
        telemetry.track_bearing_reference = Telemetry_pb2.Telemetry.TRUE_NORTH
        telemetry.vdop_gps = self.get_vdop()
        telemetry.roll = self.data['roll'] * RAD_TO_DEG
        telemetry.yaw = self.data['yaw'] * RAD_TO_DEG
        telemetry.pitch = self.data['pitch'] * RAD_TO_DEG
        telemetry.climbrate = self.get_climbrate()
        telemetry.heading = self.data['heading']
        
        return telemetry

    def __iter__(self):
        return self

    def __next__(self):
        return self.pack_telemetry()

    def send_packet(self):
        try:
            self.__grpc_stub.PostTelemetry.future(self)
        except Exception as e:
            self.__logger.error(f'Error in ANRA telemetry push ({e})')

    def new_datapoint(self, drone_id, stream_id, datapoint):
        if stream_id == ATTITUDE:
            self.data['roll'] = datapoint.roll
            self.data['pitch'] = datapoint.pitch
            self.data['yaw'] = datapoint.yaw
        elif stream_id == GPS:
            self.data['gps_0'] = datapoint
        elif stream_id == GLOBAL_FRAME:
            self.data['global_frame'] = datapoint
        elif stream_id == VELOCITY:
            self.data['velocity'] = datapoint
        elif stream_id == HEADING:
            self.data['heading'] = datapoint
        elif stream_id == GROUND_SPEED:
            self.data['ground_speed'] = datapoint
        elif stream_id == BATTERY:
            self.data['battery_level'] = datapoint.level

        self.__sim_time = int(time.time() * 1000)

        if self.__initialised:
            self.send_packet()

    def subscribes_to_streams(self):
        return [ATTITUDE, GPS, GLOBAL_FRAME, VELOCITY, HEADING, GROUND_SPEED, BATTERY]