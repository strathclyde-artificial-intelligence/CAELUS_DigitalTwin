from ProbeSystem.helper_data.subscriber import Subscriber
from ProbeSystem.helper_data.streams import *
from ..Interfaces.TimeSeriesHandler import TimeSeriesHandler
from io import StringIO
from queue import Queue

class TelemetryDisplay(Subscriber, TimeSeriesHandler):
    def __init__(self):
        super().__init__()
        self.__setup_streams = []
        self.__streams = {}
        self.__ts_handler = None
    
    def set_time_series_handler(self, ts_handler: TimeSeriesHandler):
        self.__ts_handler = ts_handler

    def new_time_series_stream_available(self, name, stream):
        self.__ts_handler.new_time_series_stream_available(name, stream)

    def __default_setup(self, stream_id):
        self.__streams[stream_id] = Queue(maxsize=5)
        self.new_time_series_stream_available(stream_id, self.__streams[stream_id])

    def __setup_attitude_stream(self):
        self.__streams['roll'] = Queue(maxsize=5)
        self.__streams['pitch'] = Queue(maxsize=5)
        self.__streams['yaw'] = Queue(maxsize=5)
        self.new_time_series_stream_available('roll', self.__streams['roll'])
        self.new_time_series_stream_available('pitch', self.__streams['pitch'])
        self.new_time_series_stream_available('yaw', self.__streams['yaw'])

    def __setup_logic_for_stream(self, stream_id):
        setup_fs = {
            ATTITUDE: self.__setup_attitude_stream
        }
        if stream_id not in setup_fs.keys():
            self.__default_setup(stream_id)
        else:
            setup_fs[stream_id]()

    def __process_datapoint(self, stream_id, datapoint):
        
        if stream_id not in self.__setup_streams:
            self.__setup_logic_for_stream(stream_id)
            self.__setup_streams.append(stream_id)

        if stream_id == ATTITUDE:
            self.__streams['roll'].put(datapoint.roll)
            self.__streams['pitch'].put(datapoint.pitch)
            self.__streams['yaw'].put(datapoint.yaw)

    def new_datapoint(self, drone_id, stream_id, datapoint):
        if self.__ts_handler is None:
            return
        self.__process_datapoint(stream_id, datapoint)

    def subscribes_to_streams(self):
        return [ATTITUDE]
