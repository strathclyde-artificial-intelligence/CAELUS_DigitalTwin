import logging
import time
from typing import Tuple
from dronekit import Vehicle, Command, mavutil

class DroneCommander():

    MAV_MODE_AUTO = 4

    @staticmethod
    def waypoints_to_string(wps, alt):
        return '\n'.join(map(lambda composite: (lambda i, wp_a: f'\t {i}: {wp_a[0][0]}, {wp_a[0][1]} ⤴ {wp_a[1]}')(*composite), enumerate(zip(wps, [alt]*len(wps)))))

    @staticmethod
    def commands_from_waypoints(waypoints: Tuple[float, float], altitude: float):
        return list(map(lambda wp: Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 1, 0, 0, 0, float('nan'), wp[1], wp[0], altitude), waypoints))

    @staticmethod
    def mission_from_waypoints(waypoints: Tuple[float, float], altitude: float):
        commands = DroneCommander.commands_from_waypoints(waypoints, altitude)
        commands.insert(0,Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 1, 0, 0, 0, float('nan'), waypoints[0][1], waypoints[0][0], altitude))
        commands.append(Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 1, 0, 0, 0, float('nan'), waypoints[-1][1], waypoints[-1][0], altitude))
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
        for c in commands:
            self.__vehicle.commands.add(c)
        self.__vehicle.commands.upload()

    def set_vehicle(self, vehicle):
        self.__vehicle = vehicle

    def set_mission(self, waypoints, altitude=30):
        self.__logger.info('Clearing vehicle remote mission')
        self.__vehicle.commands.clear()
        self.__vehicle.commands.upload()

        self.__logger.info('Constructing new missions from waypoints')
        self.__logger.info('\n'+DroneCommander.waypoints_to_string(waypoints, altitude))
        commands = DroneCommander.mission_from_waypoints(waypoints, altitude)
        
        self.__upload_vehicle_commands(commands)

        self.__logger.info('Waiting for vehicle commands acquisition')
        self.__vehicle.commands.wait_ready()
        time.sleep(2)

        self.__end_waypoint = [*waypoints[-1], altitude]

    def __wait_for_home_lock(self):
        while self.__vehicle.home_location is None:
            time.sleep(0.5)

    def __wait_for_vehicle_armable(self):
        self.__logger.info('Waiting for vehicle home lock')
        self.__wait_for_home_lock()
        self.__logger.info('Waiting for vehicle to be armable (CHECK SKIPPED!)')
        time.sleep(2)
        # while not self.__vehicle.is_armable:
        #     time.sleep(0.5)

    def start_mission(self):
        self.__wait_for_vehicle_armable()
        self.__logger.info('Starting vehicle mission')
        self.__px4_set_mode(DroneCommander.MAV_MODE_AUTO)
        self.__vehicle.armed = True
        time.sleep(1)

