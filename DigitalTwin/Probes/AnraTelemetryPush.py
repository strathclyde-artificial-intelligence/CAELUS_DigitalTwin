from ProbeSystem.helper_data.subscriber import Subscriber
from ProbeSystem.helper_data.streams import *

class AnraTelemetryPush(Subscriber):
    
    def new_datapoint(self, drone_id, stream_id, datapoint):
        print(datapoint)

    def subscribes_to_streams(self):
        return [ATTITUDE, LOCAL_FRAME]