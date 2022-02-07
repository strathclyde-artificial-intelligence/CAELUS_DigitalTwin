# import json
# from this import d
# from typing_extensions import Self

# class BaseVehicle():
    
#     ID_KEY = 'id'
#     NAME_KEY = 'name'
#     AIRFRAME_REFERENCE_KEY = 'px4_airframe_reference'

#     def __init__(self,
#         identifier: str,
#         name: str,
#         airframe_reference: str):

#         self.identifier = identifier
#         self.name = name
#         self.airframe_reference = airframe_reference

# class Multicopter(BaseVehicle):

#     LIMITS_KEY = 'limits'
#     DRONE_CONFIG_KEY = 'drone_config'

#     def __init__(self, limits, drone_config):
#         self.limits = limits
#         self.drone_config = drone_config

# class FixedWing(Multicopter):

import json
import os

ID_KEY = 'id'
NAME_KEY = 'name'
TYPE_KEY = 'type'
AIRFRAME_REFERENCE_KEY = 'px4_airframe_reference'
LIMITS_KEY = 'limits'
DRONE_CONFIG_KEY = 'drone_config'
PARAMETERS_KEY = 'px4_airframe_parameters'

PX4_FOLDER = './Dependencies/PX4-Autopilot'
SITL_CMAKE = f'{PX4_FOLDER}/platforms/posix/cmake/sitl_target.cmake'
AIRFRAMES_FOLDER = f'{PX4_FOLDER}/ROMFS/px4fmu_common/init.d-posix/airframes'
CMAKE_LISTS = f'{PX4_FOLDER}/ROMFS/px4fmu_common/init.d-posix/airframes/CMakeLists.txt'
CUSTOM_VEHICLES_FOLDER = './available_drones/'

def get_existing_vehicles(airframes_folder):
    return [name for name in os.listdir(airframes_folder) if '.' not in name]

def get_existing_airframe_numbers(airframes_folder):
    return [int(name.split('_')[0]) for name in get_existing_vehicles(airframes_folder)]

def get_new_airframe_number(airframes_folder):
    return sorted(get_existing_airframe_numbers(airframes_folder))[-1] + 1

def get_custom_vehicle_filenames(custom_vehicles_folder):
    return os.listdir(custom_vehicles_folder)

def generate_airframe_contents(vehicle_obj):
    
    def header(name, drone_type):
        return [
            "#!/bin/sh",
            f"# @name {name}",
            f"# @type {drone_type}",
            ". ${R}etc/init.d/rc.mc_defaults"
        ]

    def format_parameters(params):
        lines = []
        for key, value in params.items():
            lines.append(f'param set {key} {value}')
        return lines

    def rcs_interface_params(drone_type):
        if drone_type == 'QUADCOPTER':
            return ["set MIXER quad_x", "set PWM_OUT 1234"]
        elif drone_type == 'EVTOL_FW':
            return [
                "set MIXER_FILE etc/mixers-sitl/standard_vtol_sitl.main.mix",
                "set MIXER custom"
            ]
    
    name = vehicle_obj[NAME_KEY]
    params = vehicle_obj[PARAMETERS_KEY] if PARAMETERS_KEY in vehicle_obj else {}
    drone_type = vehicle_obj[TYPE_KEY]

    return header(name, drone_type) + format_parameters(params) + rcs_interface_params(drone_type)

def get_complete_airframe_name(airframes_folder, airframe_reference):
    return f'{get_new_airframe_number(airframes_folder)}_{airframe_reference}'

def create_new_airframe_for_vehicle(vehicle_obj, airframes_folder):
    existing_airframes = ['_'.join(name.split('_')[:1]) for name in get_existing_vehicles(airframes_folder)]
    airframe_reference = vehicle_obj[AIRFRAME_REFERENCE_KEY]
    if airframe_reference in existing_airframes:
        print(f'Airframe "{airframe_reference}" already exists. Skipping...')
    else:
        data = generate_airframe_contents(vehicle_obj)
        complete_airframe_ref_name = get_complete_airframe_name(airframes_folder, airframe_reference)
        with open(f'{AIRFRAMES_FOLDER}/{complete_airframe_ref_name}', 'w') as f:
            f.writelines([f'{line}\n' for line in data])
        print(f'Done writing airframe file "{complete_airframe_ref_name}".')

def add_model_to_sitl_target_cmake(sitl_cmake_filename, airframe_reference):
    with open(sitl_cmake_filename, 'r+') as f:
        data = f.readlines()
        line_n = data.index("set(models\n")
        data.insert(line_n+1, f'\t{airframe_reference}\n')
        f.seek(0)
        f.writelines(data)
    print(f'Added "{airframe_reference}" to {sitl_cmake_filename}')

def add_airframe_to_cmake_lists(cmake_lists, airframes_folder, airframe_reference):
    complete_airframe_name = get_complete_airframe_name(airframes_folder, airframe_reference)
    with open(cmake_lists, 'r+') as f:
        data = f.readlines()
        line_n = data.index("px4_add_romfs_files(\n")
        data.insert(line_n+1, f'\t{complete_airframe_name}\n')
        f.seek(0)
        f.writelines(data)
    print(f'Added {complete_airframe_name} to {cmake_lists}')

def sync_px4_for_vehicle_with_file(airframes_folder, sitl_cmake, cmake_lists, vehicle_file_name):
    with open(vehicle_file_name, 'r') as f:
        obj = json.loads(f.read())
        create_new_airframe_for_vehicle(obj, airframes_folder)
        add_model_to_sitl_target_cmake(sitl_cmake, obj[AIRFRAME_REFERENCE_KEY])
        add_airframe_to_cmake_lists(cmake_lists, airframes_folder, obj[AIRFRAME_REFERENCE_KEY])
