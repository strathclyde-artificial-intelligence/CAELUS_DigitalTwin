from dronekit import connect, Command, LocationGlobal
from pymavlink import mavutil
import time, sys, argparse, math
import logging

MAV_MODE_AUTO  = 4

class SimpleDroneCommander():

    @staticmethod
    def get_location_offset_meters(original_location, dNorth, dEast, alt):
        """
        Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the
        specified `original_location`. The returned Location adds the entered `alt` value to the altitude of the `original_location`.
        The function is useful when you want to move the vehicle around specifying locations relative to
        the current vehicle position.
        The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.
        For more information see:
        http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
        """
        earth_radius=6378137.0 #Radius of "spherical" earth
        #Coordinate offsets in radians
        dLat = dNorth/earth_radius
        dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

        #New position in decimal degrees
        newlat = original_location.lat + (dLat * 180/math.pi)
        newlon = original_location.lon + (dLon * 180/math.pi)
        return LocationGlobal(newlat, newlon,original_location.alt+alt)

    @staticmethod
    def commands_from_waypoints(self, waypoints, altitude=30):
        return map(lambda wp: Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 1, 0, 0, 0, 0, wp[0], wp[1], altitude))

    def __init__(self):
        self.__vehicle = None
        self.__logger = logging.getLogger(__name__)

    def px4_set_mode(self, mav_mode):
        self.__vehicle._master.mav.command_long_send(self.__vehicle._master.target_system, self.__vehicle._master.target_component,
                                                mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
                                                mav_mode,
                                                0, 0, 0, 0, 0, 0)


    def clear_vehicle_commands(self):
        # Clear previous commands
        self.__vehicle.commands.clear()

    def upload_vehicle_commands(self, commands):
        for c in commands:
            self.__vehicle.commands.add(c)
        self.__vehicle.commands.upload()
    
    @staticmethod
    def sample_mission_commands(home):
        cmds = []
        # takeoff to 10 meters
        wp = SimpleDroneCommander.get_location_offset_meters(home, 0, 0, 10)
        cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 1, 0, 0, 0, 0, wp.lat, wp.lon, wp.alt)
        cmds.append(cmd)

        # move 10 meters north
        wp = SimpleDroneCommander.get_location_offset_meters(wp, 10, 0, 0)
        cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 1, 0, 0, 0, 0, wp.lat, wp.lon, wp.alt)
        cmds.append(cmd)

        # move 10 meters east
        wp = SimpleDroneCommander.get_location_offset_meters(wp, 0, 10, 0)
        cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 1, 0, 0, 0, 0, wp.lat, wp.lon, wp.alt)
        cmds.append(cmd)

        # move 10 meters south
        wp = SimpleDroneCommander.get_location_offset_meters(wp, -10, 0, 0)
        cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 1, 0, 0, 0, 0, wp.lat, wp.lon, wp.alt)
        cmds.append(cmd)

        # move 10 meters west
        wp = SimpleDroneCommander.get_location_offset_meters(wp, 0, -10, 0)
        cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 1, 0, 0, 0, 0, wp.lat, wp.lon, wp.alt)
        cmds.append(cmd)

        # land
        wp = SimpleDroneCommander.get_location_offset_meters(home, 0, 0, 10)
        cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 1, 0, 0, 0, 0, wp.lat, wp.lon, wp.alt)
        cmds.append(cmd)

        return cmds

    def wait_for_home_lock(self):
        while self.__vehicle.home_location is None:
            print('polling home...')
            time.sleep(0.5)

    def execute_sample_mission(self):

        self.__logger.info('Executing sample mission')
        self.wait_for_home_lock()
        self.px4_set_mode(MAV_MODE_AUTO)
        self.clear_vehicle_commands()
        time.sleep(1)
        cmds = SimpleDroneCommander.sample_mission_commands(self.__vehicle.location.global_relative_frame)
        self.upload_vehicle_commands(cmds)
        time.sleep(5)
        # Arm vehicle
        self.__vehicle.armed = True

        # monitor mission execution
        nextwaypoint = self.__vehicle.commands.next
        while nextwaypoint < len(self.__vehicle.commands):
            if self.__vehicle.commands.next > nextwaypoint:
                display_seq = self.__vehicle.commands.next+1
                print("Moving to waypoint %s" % display_seq)
                nextwaypoint = self.__vehicle.commands.next
            time.sleep(1)

        # wait for the self.__vehicle to land
        while self.__vehicle.commands.next > 0:
            time.sleep(1)

        # Disarm self.__vehicle
        self.__vehicle.armed = False
        time.sleep(1)

        # Close self.__vehicle object before exiting script
        self.__vehicle.close()
        time.sleep(1)

    def execute_mission(self, waypoints):
        self.__logger.info('Executing mission')
        self.wait_for_home_lock()

        self.px4_set_mode(MAV_MODE_AUTO)
        self.clear_vehicle_commands()
        time.sleep(1)
        
        commands = SimpleDroneCommander.commands_from_waypoints(waypoints)
        self.upload_vehicle_commands(commands)

        time.sleep(5)
        # monitor mission execution
        nextwaypoint = self.__vehicle.commands.next
        while nextwaypoint < len(self.__vehicle.commands):
            if self.__vehicle.commands.next > nextwaypoint:
                display_seq = self.__vehicle.commands.next+1
                print("Moving to waypoint %s" % display_seq)
                nextwaypoint = self.__vehicle.commands.next
            time.sleep(1)

        # wait for the self.__vehicle to land
        while self.__vehicle.commands.next > 0:
            time.sleep(1)

        # Disarm self.__vehicle
        self.__vehicle.armed = False
        time.sleep(1)

        # Close self.__vehicle object before exiting script
        # self.__vehicle.close()
        # time.sleep(1)

    def set_vehicle(self, vehicle):
        self.__vehicle = vehicle