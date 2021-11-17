import threading
import json

class MissionWriter(threading.Thread):
    def __init__(self, mission_id):
        super().__init__()
        
        self.name = 'MissionWriter'
        self.daemon = True

        self.data = {
            'payload_temp':[],
            'battery_level':[],
        }

        self.__mission_id = mission_id
        self.__thermal_model = None
        self.__battery = None
        self.__esc = None

    def run(self):
        while True:
            new_temp = self.__thermal_model.get_payload_temperature()
            new_batt = self.__battery.get_battery_level()
            if len(self.data['payload_temp']) == 0 or new_temp != self.data['payload_temp'][-1]:
                self.data['payload_temp'].append(new_temp)
            if len(self.data['battery_level']) == 0 or new_batt != self.data['battery_level'][-1]:
                self.data['battery_level'].append(new_batt)

    def set_thermal_model(self, tm):
        self.__thermal_model = tm

    def set_battery(self, b):
        self.__battery = b

    def set_esc(self, esc):
        self.__esc = esc

    def save(self, filename=None):
        if filename is None:
            filename = f'mission_{self.__mission_id}.txt'
        with open(filename, 'w') as f:
            f.write(json.dumps(self.data))