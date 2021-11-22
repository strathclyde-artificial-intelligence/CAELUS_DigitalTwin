from .Interfaces.TimeSeriesHandler import TimeSeriesHandler
import threading
from queue import Queue
from time import sleep

class TelemetryFeedback(threading.Thread, TimeSeriesHandler):
    def __init__(self):
        super().__init__()
        
        self.name = 'Telemetry Feedback'
        self.daemon = True

        self.__streams = {}
        self.__thermal_model = None
        self.__battery = None
        self.__ts_handler = None
        
    def set_time_series_handler(self, ts_handler: TimeSeriesHandler):
        self.__ts_handler = ts_handler

    def new_time_series_stream_available(self, name, stream):
        if self.__ts_handler is not None:
            self.__ts_handler.new_time_series_stream_available(name, stream)

    def __default_setup(self, stream_id):
        self.__streams[stream_id] = Queue(maxsize=5)
        self.new_time_series_stream_available(stream_id, self.__streams[stream_id])

    def run(self):
        self.__default_setup('battery_level')
        self.__default_setup('payload_temperature')
        while True:
            temp = self.__thermal_model.get_payload_temperature()
            batt = self.__battery.get_battery_level()
            self.__streams['battery_level'].put(batt)
            self.__streams['payload_temperature'].put(temp)
            sleep(0.2)

    def set_thermal_model(self, tm):
        self.__thermal_model = tm

    def set_battery(self, b):
        self.__battery = b
