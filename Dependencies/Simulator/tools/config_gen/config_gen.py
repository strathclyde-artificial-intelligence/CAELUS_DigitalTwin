import PySimpleGUI as sg
import json

SAVE_BUTTON_EVENT = 'SAVE_EVT'

class Config():
    AVAILABLE_PARAMS = {
        'mass': 'Vehicle mass',
        'jxx': 'Jxx (Rolling moment of inertia)',
        'jyy': 'Jyy (Pitching moment of inertia)',
        'jzz': 'Jzz (Yawing moment of inertia)',
        'vtol_komega': 'KΩ (VTOL Rotor thrust to omega coefficient)',
        'vtol_kv': 'Kv (VTOL Rotor rotational velocity coefficient)',
        'vtol_klift': 'Kf (VTOL Rotor thrust lift coefficient)',
        'vtol_tdrag': 'tdrag (VTOL Rotor torque drag)',
        'vtol_tau': 'τf (VTOL Rotor thrust model time constant)',
        'vtol_lcog': 'l (VTOL Rotor distance to CoG)',
        'thruster_komega': 'KΩ (Thruster Rotor thrust to omega coefficient)',
        'thruster_kv': 'Kv (Thruster Rotor rotational velocity coefficient)',
        'thruster_klift': 'Kf (Thruster Rotor thrust lift coefficient)',
        'thruster_tdrag': 'tdrag (Thruster Rotor torque drag)',
        'thruster_tau': 'τf (Thruster Rotor thrust model time constant)',
        'thruster_lcog': 'l (Thruster Rotor distance to CoG)'
    }
    
    @staticmethod
    def FromFile(fname):
        print(f'Loading config file "{fname}"')
        with open(fname, 'r') as f:
            data = json.loads(f.read())    
            return Config(fname, data)

    def ensure_all_numbers(self):
        for k,v in self.get_items():
            self.json_data[k] = float(v)
            
    def __init__(self, file_name, json_data):
        self.file_name = file_name
        self.json_data = json_data
        self.ensure_all_numbers()
    
    def save(self):
        self.ensure_all_numbers()
        print(f'Saving config to file "{self.file_name}"')
        with open(self.file_name, 'w') as f:
            json.dump(self.json_data, f)

    def get_keys(self):
        return self.json_data.keys()

    def get_items(self):
        return self.json_data.items()
        
def make_labels(config):
    return [sg.Text(f'{Config.AVAILABLE_PARAMS[k]}: ') for k,_ in config.get_items()]

def make_text_boxes(config):
    return [sg.InputText(v, key=k, enable_events=True) for k,v in config.get_items()]

def calc_hover_pwm(config):
    return (config.json_data['mass'] * 9.81 / 4) / (config.json_data['vtol_kv']**2 * config.json_data['vtol_komega'])

def make_px4_params(config):
    return [
        # sg.Text(f'MPC_THR_HOVER'),
        # sg.InputText(calc_hover_pwm(config), key='MPC_THR_HOVER')
    ]
    
def make_layout(config):
    labels = make_labels(config)
    text_boxes = make_text_boxes(config)
    px4_params = make_px4_params(config)
    save_btn = sg.Button("Save config", key=SAVE_BUTTON_EVENT, enable_events=True)
    
    return list(zip(labels, text_boxes)) + [[px4_params]] + [[save_btn]]

def process_changes(values, config):
    config.json_data = values

def make_window(config):
    window = sg.Window(title="Config Editor", layout=make_layout(config))
    return window

def event_loop(config, window):
    print("Start event loop")
    while True:
        event, values = window.read()
        if event in config.get_keys():
            process_changes(values, config)
        if event == SAVE_BUTTON_EVENT:
            config.save()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break      

def new_config(name = 'Untitled'):
    return Config(name, {key:0 for key in Config.AVAILABLE_PARAMS.keys()})

config = Config.FromFile('../../drone_models/small')
window = make_window(config)
event_loop(config, window)