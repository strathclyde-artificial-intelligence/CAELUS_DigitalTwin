from ProbeSystem.helper_data.subscriber import Subscriber
from ProbeSystem.helper_data.streams import *
from dataclasses import dataclass, asdict
from typing import List
from datetime import datetime
import socket
import threading
import time
import json
import uuid
from math import pi

M_TO_FT = 3.281
RAD_TO_DEG = 180 / pi
M_PER_SEC_TO_KNOTS = 1.944

@dataclass(frozen=True)
class AltitudeModel():
    altitude_value: float # is this AMSL?
    vertical_reference: str # use "W84"
    units_of_measure: str # can use "FT", ask for meters, probably "FT"
    source: str # "ONBOARD_SENSOR"
    
    def serialise(self):
        return asdict(self)

@dataclass(frozen=True)
class PointModel():
    type: str # "Point"
    coordinates: List[float] # lon lat (DDeg)

    def serialise(self):
        return asdict(self)

@dataclass(frozen=True)
class AnraTelemetryPacket():
    roll: float
    pitch: float
    yaw: float
    climbrate: float # m/s
    heading: float # DDeg
    battery_remaining: int # CHANGE!!
    mode: str # quadrotor mode - fixed wing mode
    registration: str # drone registration id (registration_number from SmartSkies.Drone)
    enroute_positions_id: str # uuidv4 of positions? (Generate UUID)
    altitude_gps: AltitudeModel
    altitude_num_gps_satellites: int # number of satellites
    operation_id: str # uuidv4 of the operation (operation_id)
    control_area_id: str
    reference_number: str # the operation reference number?
    hdop_gps: float
    vdop_gps: float
    location: PointModel # current location
    time_measured: str # yyy-MM-ddTHH:mm:ssZ time of the measuring
    time_sent: str # yyy-MM-ddTHH:mm:ssZ time of sending data
    track_bearning: float # yaw wrt north
    track_bearning_reference: str # TRUE_NORTH of MAGNETIC_NORTH
    track_bearing_uom: str # "DEG"
    track_ground_speed: float # horizontal ground speed
    track_ground_speed_units: str # use "KT" or ask for meters/s
    payload_temperature: float # in C°

    def serialise(self):
        return {**asdict(self), 
        **self.altitude_gps.serialise(),
        **self.location.serialise()}

class AnraTelemetryPush(Subscriber):

    def __init__(self):

        super().__init__()
        self.__should_stop = False

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

        self.__remote_ip = '54.243.221.198'
        self.__remote_port = 51001
        self.__send_thread = None

    def start_sending_telemetry(self,
        drone_registration,
        operation_id,
        control_area_id,
        reference_number,
        dis_token):

        self.drone_registration = drone_registration
        self.operation_id = operation_id
        self.control_aread_id = control_area_id
        self.reference_number = reference_number
        self.__dis_token = dis_token

        self.__send_thread = self.setup_send_thread()

    def stop_sending_telemetry(self):
        self.__should_stop = True
        self.drone_registration = None
        self.operation_id = None
        self.control_aread_id = None
        self.reference_number = None
        self.__dis_token = None


    def setup_send_thread(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        t = threading.Thread(target=self.send_packet, args=())
        t.name = 'Anra TelemetryPush'
        t.daemon = True
        t.start()

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
            return AltitudeModel(
            0,
            'W84',
            'FT',
            'ONBOARD_SENSOR'
        )
        return AltitudeModel(
            self.data['global_frame'].alt * M_TO_FT,
            'W84',
            'FT',
            'ONBOARD_SENSOR'
        )

    def pack_location(self):
        if self.data['global_frame'] is None:
            return PointModel(
                'Point',
                [0,0]
        )
        return PointModel(
            'Point',
            [self.data['global_frame'].lon, self.data['global_frame'].lat]
        )

    def get_timestamp(self):
        return datetime.now().isoformat()

    def pack_telemetry(self):
        return AnraTelemetryPacket(
            self.data['roll'] * RAD_TO_DEG,
            self.data['pitch'] * RAD_TO_DEG,
            self.data['yaw'] * RAD_TO_DEG,
            self.get_climbrate(),
            self.data['heading'],
            100,
            'quadrotor',
            self.drone_registration,
            str(uuid.uuid4()),
            self.pack_altitude(),
            self.get_sat_number(),
            self.operation_id,
            self.control_aread_id,
            self.reference_number,
            self.get_hdop(),
            self.get_vdop(),
            self.pack_location(),
            self.get_timestamp(),
            self.get_timestamp(),
            self.data['heading'], # why duplicate?
            'TRUE_NORTH',
            'DEG',
            self.data['ground_speed'] * M_PER_SEC_TO_KNOTS,
            'KT',
            self.__payload_handler.get_payload_temperature() if self.__payload_handler is not None else 25
        )

    def send_packet(self):
        while not self.__should_stop:
            js_obj = self.pack_telemetry().serialise()
            packet = json.dumps({
                'Token': self.__dis_token,
                'DataType': 'Telemetry',
                'Data':json.dumps(js_obj)
            })
            self.__socket.sendto(bytes(packet, "utf-8"), (self.__remote_ip, self.__remote_port))
            time.sleep(0.1)

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

    def set_payload_handler(self, pl):
        self.__payload_handler = pl

    def subscribes_to_streams(self):
        return [ATTITUDE, GPS, GLOBAL_FRAME, VELOCITY, HEADING, GROUND_SPEED]