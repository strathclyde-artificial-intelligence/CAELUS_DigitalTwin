import logging
import time
from typing import Tuple
from dronekit import Vehicle, Command, mavutil

class DroneCommander():

    MAV_MODE_AUTO = 4

    @staticmethod
    def waypoints_to_string(wps):
        return '\n'.join(map(lambda composite: (lambda i, wp_a: f'\t {i}: {wp_a[0]}, {wp_a[1]} ⤴ {wp_a[2]}')(*composite), enumerate(wps)))

    @staticmethod
    def commands_from_waypoints(waypoints: Tuple[float, float, float]):
        return list(map(lambda wp: Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 1, 0, 0, 0, float('nan'), wp[1], wp[0], wp[2]), waypoints))

    @staticmethod
    def mission_from_waypoints(waypoints: Tuple[float, float, float]):
        commands = DroneCommander.commands_from_waypoints(waypoints[:-1]) # Last waypoint should be landing
        commands.insert(0,Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 1, 0, 0, 0, float('nan'), waypoints[0][1], waypoints[0][0], waypoints[0][2]))
        commands.append(Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL, mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 1, 0, 0, 0, float('nan'), waypoints[-1][1], waypoints[-1][0], waypoints[-1][2]))
        return commands

    def set_roi(self, location):
        # create the MAV_CMD_DO_SET_ROI command
        msg = self.__vehicle.message_factory.command_long_encode(
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_CMD_DO_SET_ROI, #command
            0, #confirmation
            0, 0, 0, 0, #params 1-4
            *location
            )
        # send command to vehicle
        self.__vehicle.send_mavlink(msg)

    def __init__(self):
        self.__vehicle: Vehicle = None
        self.__logger = logging.getLogger(__name__)
    
    def __px4_set_mode(self, mav_mode):
        self.__vehicle._master.mav.command_long_send(self.__vehicle._master.target_system, self.__vehicle._master.target_component,
                                                mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
                                                mav_mode,
                                                0, 0, 0, 0, 0, 0)

    def __setup_vehicle(self):
        pass

    def __upload_vehicle_commands(self, commands):
        self.__logger.info('Waiting for vehicle to be ready for upload')
        self.__vehicle.wait_ready()
        
        self.__logger.info('Uploading commands')
        cmd_n = len(commands)
        self.__vehicle._master.first_byte = True
        for i,c in enumerate(commands):
            c.seq = i+1
            self.__vehicle._wploader.add(c)
        
        self.__vehicle._master.waypoint_clear_all_send()
        self.__vehicle._master.waypoint_count_send(cmd_n)

        for i in range(cmd_n):
            while True:
                try:
                    msg = self.__vehicle._master.recv_match(type=['MISSION_REQUEST'],blocking=True) 
                    self.__vehicle._master.mav.send(self.__vehicle._wploader.wp(msg.seq))
                    break
                except:
                    pass
            print(f"Uploaded mission item {i}")

        self.__logger.info(f'Done uploading mission ({cmd_n} items)')
        self.__vehicle._wp_uploaded = None
        self.__vehicle._wpts_dirty = False
        self.__vehicle.wait_ready()
        

    def set_vehicle(self, vehicle):
        self.__vehicle = vehicle

    def set_mission(self, waypoints):
        
        self.__mission_waypoints = waypoints
        
        self.__logger.info('Constructing new missions from waypoints')
        self.__logger.info('\n'+DroneCommander.waypoints_to_string(waypoints))
        commands = DroneCommander.mission_from_waypoints(waypoints)
        
        self.__vehicle.commands.clear()
        self.__vehicle.commands.upload()
        

        for c in commands:
            self.__vehicle.commands.add(c)
        print(f'Uploading {len(commands)} commands...')
        self.__upload_vehicle_commands(commands)
        # self.__vehicle.commands.upload()
        print(f'Done uploading!')

        self.__vehicle.commands.wait_ready()

        self.__logger.info('Waiting for vehicle commands acquisition')

        self.__end_waypoint = waypoints[-1]

    def wait_for_home_lock(self):
        while self.__vehicle.home_location is None:
            time.sleep(0.5)

    def __wait_for_vehicle_armable(self):
        self.__logger.info('Waiting for vehicle home lock')
        self.wait_for_home_lock()
        print(f'Home location: {self.__vehicle.home_location}')
        self.__logger.info('Waiting for vehicle to be armable (CHECK SKIPPED!)')
        time.sleep(2)

    def start_mission(self):
        self.__wait_for_vehicle_armable()
        self.__logger.info('Starting vehicle mission')
        self.__px4_set_mode(DroneCommander.MAV_MODE_AUTO)
        # +2 to account for takeoff nad landing items
        self.__vehicle.prepare_for_mission(len(self.__mission_waypoints)+2)
        self.__vehicle.armed = True

