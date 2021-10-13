from ..helper_data.subscriber import Subscriber
from ..helper_data.streams import *

class AnraTelemetrySerialiser():
    def __init__(self):
        self.attitude = (0,0,0)
        

class AnraTelemetryPush(Subscriber):
    
    def new_datapoint(self, drone_id, stream_id, datapoint):
        print(datapoint)

    def subscribes_to_streams(self):
        return [ATTITUDE]