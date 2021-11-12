import json
import logging
from typing import List, Tuple, Dict
from PySmartSkies.Models.Drone import Drone

KEY_NOT_FOUND = lambda k,d: f'Key {k} not found in dict {d}'
KEY_WRONG_TYPE = lambda k,d,t: f'Key {k} is present but with the wrong type (Expected {t}, got {type(d[k])})'

def get(d, k, fail=False):
    if k not in d:
        if fail:
            raise Exception(KEY_NOT_FOUND(k,d))
        else:
            logging.getLogger().warn(KEY_NOT_FOUND(k,d))
    else:
        return d[k]

class Unpackable():
    @classmethod
    def from_json_file(cls, file):
        with open(file, 'r') as f:
            s = json.loads(f.read())
            return cls(s)

class ControllerPayload(Unpackable):
    
    def __init__(self, config_dict):
        self.waypoints: Tuple[float, float, float] = get(config_dict, 'waypoints')
        self.operation_id: str = get(config_dict, 'operation_id')
        self.control_area_id: str = get(config_dict, 'control_area_id')
        self.operation_reference_number: str = get(config_dict, 'operation_reference_number')
        self.drone_id: str = get(config_dict, 'drone_id')
        self.drone_registration_number: str = get(config_dict, 'drone_registration_number')
        self.dis_auth_token: str = get(config_dict, 'dis_auth_token')

class SimulatorPayload(Unpackable):

    def __init__(self, config_dict):
        self.drone_config: Dict[str, float] = get(config_dict, 'drone_config')
        self.g_acceleration: float = get(config_dict, 'g_acceleration')
        self.initial_lon_lat_alt: Tuple[float, float, float] = get(config_dict, 'initial_lon_lat_alt')
        self.thermal_model_timestep: float = get(config_dict, 'thermal_model_timestep')
        self.aeroacoustic_model_timestep: float = get(config_dict, 'aeroacoustic_model_timestep')