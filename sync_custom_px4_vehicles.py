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
            ". ${R}etc/init.d/rc.mc_defaults" if drone_type == "QUADCOPTER" else ". ${R}etc/init.d/rc.vtol_defaults",
            ". ${R}etc/init.d-posix/airframes/4200_custom_quad" if drone_type == "QUADCOPTER" else ". ${R}etc/init.d-posix/airframes/4201_custom_evtol"
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

def create_new_airframe_for_vehicle(cmake_lists, airframes_folder, vehicle_obj):
    response = None
    existing_airframes = ['_'.join(name.split('_')[1:]) for name in get_existing_vehicles(airframes_folder)]
    airframe_reference = vehicle_obj[AIRFRAME_REFERENCE_KEY]
    if airframe_reference in existing_airframes:
        print(f'Airframe "{airframe_reference}" already exists.')
        response = input(f'Do you want to override the existing file with the new configuration? (enter to skip, y to override)')
        if response != 'y':
            return
    data = generate_airframe_contents(vehicle_obj)
    complete_airframe_ref_name = get_complete_airframe_name(airframes_folder, airframe_reference)
    with open(f'{AIRFRAMES_FOLDER}/{complete_airframe_ref_name}', 'w') as f:
        f.writelines([f'{line}\n' for line in data])
    print(f'Done writing airframe file "{complete_airframe_ref_name}".')
    if response is None:
        add_airframe_to_cmake_lists(cmake_lists, complete_airframe_ref_name)

def add_model_to_sitl_target_cmake(sitl_cmake_filename, airframe_reference):
    model_string = f'\t{airframe_reference}\n'
    with open(sitl_cmake_filename, 'r+') as f:
        data = f.readlines()
        if model_string in data:
            print(f'Model string "{airframe_reference}" already in sitl_cmake. Skipping...')
            return
        line_n = data.index("set(models\n")
        data.insert(line_n+1, model_string)
        f.seek(0)
        f.writelines(data)
    print(f'Added "{airframe_reference}" to {sitl_cmake_filename}')

def add_airframe_to_cmake_lists(cmake_lists, complete_airframe_name):
    airframe_string = f'\t{complete_airframe_name}\n'
    with open(cmake_lists, 'r+') as f:
        data = f.readlines()
        line_n = data.index("px4_add_romfs_files(\n")
        data.insert(line_n+1, airframe_string)
        f.seek(0)
        f.writelines(data)
    print(f'Added {complete_airframe_name} to {cmake_lists}')

def sync_px4_for_vehicle_with_file(airframes_folder, sitl_cmake, cmake_lists, vehicle_file_name):
    with open(vehicle_file_name, 'r') as f:
        obj = json.loads(f.read())
        create_new_airframe_for_vehicle(cmake_lists, airframes_folder, obj)
        add_model_to_sitl_target_cmake(sitl_cmake, obj[AIRFRAME_REFERENCE_KEY])

def prompt_for_warning_and_agreement():
    print("[WARNING] This script is meant to be used as a shortcut to the manual PX4 vehicle config creation.")
    print("It performs **unsafe** file edits within the PX4 folder.")
    print("**BACKUP** any change in the PX4 folder before running the script!")
    input("(Press enter to continue or CTRL+C to terminate this script)")
    
if __name__ == '__main__':
    prompt_for_warning_and_agreement()
    all_drones = os.listdir(CUSTOM_VEHICLES_FOLDER)
    for drone_file in all_drones:
        try:
            print(f'Sync-ing "{drone_file}"')
            sync_px4_for_vehicle_with_file(AIRFRAMES_FOLDER, SITL_CMAKE, CMAKE_LISTS, f'{CUSTOM_VEHICLES_FOLDER}/{drone_file}')
            print("="*20 + "\n")
        except Exception as e:
            print(f'Error in sync-ing "{drone_file}":')
            print(e)