from ..helper_data.subscriber import Subscriber
from ..helper_data.streams import *
from dataclasses import dataclass, is_dataclass, asdict
from typing import Tuple
from tinydb import TinyDB

@dataclass(repr=True, frozen=True)
class DroneState():
    drone_id: str
    timestamp: str
    is_armed: bool
    flight_mode: str
    position: Tuple[float, float, float, float]

class DatabaseSubscriber(Subscriber):
    
    def __init__(self):
        self.last_stream_data = {}
        self.db = TinyDB('./db.json')

    def save_current_drone_state(self, drone_id):
        drone_state = DroneState(**self.last_stream_data[drone_id])
        print(f"Saving new drone state for drone {drone_id}: ", drone_state)
        self.db.table(drone_id).insert(asdict(drone_state))

    def process_datapoint(self, drone_id, stream_id, datapoint):
        data, timestamp = datapoint
        
        if drone_id not in self.last_stream_data:
            self.last_stream_data[drone_id] = {
                'drone_id':drone_id,
                'timestamp': None,
                'is_armed': False,
                'flight_mode': None,
                'position': None,
            }
            
        state_dict = self.last_stream_data[drone_id]
        state_dict['timestamp'] = timestamp

        if stream_id == ARMED:
            state_dict['is_armed'] = data
        elif stream_id == VEHICLE_MODE:
            state_dict['flight_mode'] = data.name
        elif stream_id == GPS:
            state_dict['position'] = (
                data.latitude_deg,
                data.longitude_deg,
                data.absolute_altitude_m,
                data.relative_altitude_m
            )
        self.save_current_drone_state(drone_id)

    def new_datapoint(self, drone_id, stream_id, datapoint):
        self.last_stream_data[stream_id] = self.process_datapoint(drone_id, stream_id, datapoint)

    def subscribes_to_streams(self):
        return []