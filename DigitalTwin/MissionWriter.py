import threading
import json
import time

class MissionWriter(threading.Thread):

    @staticmethod
    def empty_data():
        return {
            'payload_temp':[],
            'battery_level':[],
            'flight_time':0.0
        }

    def __init__(self, mission_id, flush_every_seconds=5):
        super().__init__()
        
        self.name = 'MissionWriter'
        self.daemon = True

        self.data = MissionWriter.empty_data()

        self.__mission_id = mission_id
        self.__thermal_model = None
        self.__battery = None
        self.__esc = None
        self.__flight_time_sec = 0.0
        self.__flush_every_seconds = flush_every_seconds

    def run(self):
        last = time.time()
        while True:
            new_temp = self.__thermal_model.get_payload_temperature()
            new_batt = self.__battery.get_battery_level()
            if len(self.data['payload_temp']) == 0 or new_temp != self.data['payload_temp'][-1]:
                self.data['payload_temp'].append(new_temp)
            if len(self.data['battery_level']) == 0 or new_batt != self.data['battery_level'][-1]:
                self.data['battery_level'].append(new_batt)
            self.data['flight_time'] = self.__thermal_model.get_payload_time() / 1000000
            now = time.time()
            elapsed = now - last
            if elapsed > self.__flush_every_seconds:
                self.__flush_data()

    def set_thermal_model(self, tm):
        self.__thermal_model = tm

    def set_battery(self, b):
        self.__battery = b

    def set_esc(self, esc):
        self.__esc = esc

    def save(self, filename=None):
        if filename is None:
            filename = f'mission_{self.__mission_id}.simout'
        with open(filename, 'w') as f:
            f.write(json.dumps(self.data))