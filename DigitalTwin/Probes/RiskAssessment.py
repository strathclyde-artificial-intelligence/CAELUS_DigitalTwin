from ProbeSystem.helper_data.subscriber import Subscriber
from ProbeSystem.helper_data.streams import *

from DigitalTwin.Interfaces.DBAdapter import DBAdapter

class RiskAssessment(Subscriber):
    
    TIMESTAMP = 'timestamp'
    POSITION = 'position'
    VELOCITY = 'velocity'
    ROTATION = 'rotation'
    ROTATION_RATE = 'rotation_rate'

    def __init__(self, writer: DBAdapter, publish_frequency_s = 1): # 1 second default
        super().__init__()
        
        self.__aggregated_data = {
            RiskAssessment.TIMESTAMP: None,
            RiskAssessment.POSITION: None, # LatLonAlt
            RiskAssessment.VELOCITY: None, # NED
            RiskAssessment.ROTATION: None, # quaternions
            RiskAssessment.ROTATION_RATE: None # Gyro
        }

        self.__writer = writer
        self.__last_publish_time = 0
        self.__publish_frequency_s = publish_frequency_s

    def __validate_data(self):
        return True if not (None in self.__aggregated_data.values()) else False

    def __data_summary(self):
        if self.__validate_data():
            return self.__aggregated_data
        return None

    def __aggregate_data(self, stream_id, datapoint):
        if stream_id == SYSTEM_TIME:
            self.__aggregated_data[RiskAssessment.TIMESTAMP] = datapoint.time_boot_ms / 1000.0 # ms to sec
        elif stream_id == VELOCITY:
            self.__aggregated_data[RiskAssessment.VELOCITY] = datapoint
        elif stream_id == ATTITUDE_QUATERNION:
            self.__aggregated_data[RiskAssessment.ROTATION] = {
                'q1': datapoint.q1,
                'q2': datapoint.q2,
                'q3': datapoint.q3,
                'q4': datapoint.q4
            }
        elif stream_id == GYRO:
            self.__aggregated_data[RiskAssessment.ROTATION_RATE] = {
                'yawspeed': datapoint.yawspeed,
                'pitchspeed': datapoint.pitchspeed,
                'rollspeed': datapoint.rollspeed
            }   
        elif stream_id == GLOBAL_FRAME:
            self.__aggregated_data[RiskAssessment.POSITION] = {
                'lat': datapoint.lat,
                'lon': datapoint.lon,
                'alt': datapoint.alt
            }

    def new_datapoint(self, drone_id, stream_id, datapoint):
        self.__aggregate_data(stream_id, datapoint)
        data = self.__data_summary()        
        if data is not None and data['timestamp'] >= self.__last_publish_time+self.__publish_frequency_s:
            self.__writer.store({'risk_assessment_data': {**data}})
            self.__last_publish_time = data['timestamp']
                    
    def subscribes_to_streams(self):
        return [SYSTEM_TIME, VELOCITY, ATTITUDE_QUATERNION, GLOBAL_FRAME, GYRO]