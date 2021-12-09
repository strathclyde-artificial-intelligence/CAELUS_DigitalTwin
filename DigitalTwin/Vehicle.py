import logging
from dronekit import Vehicle as DronekitVehicle
from threading import Thread
import time

from DigitalTwin.Interfaces.DBAdapter import DBAdapter

class HilActuatorControls(object):
    """
    The message definition is here: https://mavlink.io/en/messages/common.html#HIL_ACTUATOR_CONTROLS
    
    :param time_usec: Timestamp (microseconds since system boot).
    :param controls: Control outputs -1 .. 1. Channel assignment depends on the simulated hardware.
    :param mode: System mode. Includes arming state. (https://mavlink.io/en/messages/common.html#MAV_MODE_FLAG)
    :param flags: Flags as bitfield, 1: indicate simulation using lockstep.
    """
    def __init__(self, time_usec=None, controls=None, mode=None, flags=None):
        self.time_usec = time_usec
        self.controls = controls
        self.mode = mode
        self.flags = flags
        
    def __str__(self):
        """
        String representation used to print the RawIMU object. 
        """
        return f"HIL_ACTUATOR_CONTROLS: time_boot_us={self.time_usec}, controls={self.controls}"
   
class SystemTime(object):
    """
    The message definition is here: https://mavlink.io/en/messages/common.html#SYSTEM_TIME
    
    :param time_unix_usec Timestamp (UNIX epoch time).
    :param time_boot_us: Timestamp (microseconds since system boot).
    """
    def __init__(self, time_unix_usec=None, time_boot_ms=None):
        self.time_unix_usec = time_unix_usec
        self.time_boot_ms = time_boot_ms
        
    def __str__(self):
        """
        String representation used to print the RawIMU object. 
        """
        return f"SYSTEM_TIME: time_unix_usec={self.time_unix_usec}, time_boot_ms={self.time_boot_ms}"
   
class Vehicle(DronekitVehicle):
    DB_MISSION_STATUS = 'waypoint_completion'
    TAKING_OFF = 0
    TAKEOFF_COMPLETE = 1
    CRUISING = 2
    LANDING = 3
    LANDING_COMPLETE = 4

    mission_status = [TAKING_OFF, TAKEOFF_COMPLETE, CRUISING, LANDING, LANDING_COMPLETE]

    def __init__(self, *args):
        super().__init__(*args)

        self.__mission_ended = False
        self.__logger = logging.getLogger()
        self.__controller = None
        self.__last_wp = -1
        self.__mission_hanlder_queues = []
        self.__writer = None

        self._hil_actuator_controls = HilActuatorControls()
        @self.on_message('HIL_ACTUATOR_CONTROLS')
        def listener(self, name, message):
            self._hil_actuator_controls.time_usec =message.time_usec
            self._hil_actuator_controls.controls=message.controls
            self._hil_actuator_controls.mode=message.mode
            self._hil_actuator_controls.flags=message.flags
            self.notify_attribute_listeners('hil_actuator_controls', self._hil_actuator_controls)         

        self._system_time = SystemTime()
        @self.on_message('SYSTEM_TIME')
        def listener(self, name, message):
            self._system_time.time_boot_ms=message.time_boot_ms
            self._system_time.time_unix_usec=message.time_unix_usec
            self.notify_attribute_listeners('system_time', self._system_time) 
    
    def __mission_status_to_string(self, s):
        return {
            0: 'Takeoff',
            1: 'Takeoff complete',
            2: 'Cruising',
            3: 'Landing',
            4: 'Landing complete'
        }[s]

    def add_mission_hanlder_queue(self, queue):
        self.__mission_hanlder_queues.append(queue)

    def publish_mission_status(self, status):
        if status not in Vehicle.mission_status:
            self.__logger.warn("Tried to publish an invalid mission status!")
        self.__logger.info(f'Mission status updated: {self.__mission_status_to_string(status)}')
        if self.__writer is not None:
            self.__writer.store({Vehicle.DB_MISSION_STATUS:f"{max(0, self.commands.next-1)}/{self.__mission_items_n}"}, series=False)
        for q in self.__mission_hanlder_queues:
            q.put(status)
        if status == Vehicle.LANDING_COMPLETE:
            if self.__controller is None:
                self.__logger.warn('Mission complete but no handler to notify!')
            else:
                self.__controller.mission_complete()

    def __process_mission_status(self, waypoint_n):
        if self.__last_wp > 0 and waypoint_n == 0:
            self.publish_mission_status(Vehicle.LANDING_COMPLETE)
        elif waypoint_n == 0:
            self.publish_mission_status(Vehicle.TAKING_OFF)
        elif waypoint_n == self.__mission_items_n - 1:
            self.publish_mission_status(Vehicle.LANDING)
        elif waypoint_n > 0:
            if self.__last_wp == 0:
                self.publish_mission_status(Vehicle.TAKEOFF_COMPLETE)
            self.publish_mission_status(Vehicle.CRUISING)
        else:
            self.__logger.warn(f'Unrecognised waypoint number: {waypoint_n}')
        self.__last_wp = waypoint_n

    def mission_status_update(self):
        while True:
            new_waypoint = self.commands.next
            if self.__last_wp != new_waypoint:
                self.__process_mission_status(new_waypoint)
            time.sleep(1)

    def prepare_for_mission(self, mission_items_n):

        self.__logger.info(f"Preparing for mission with {mission_items_n} items")
        self.__mission_items_n = mission_items_n
        self.__mission_ended = False
        
        self.__mission_completion_thread = Thread(target=self.mission_status_update)
        self.__mission_completion_thread.name = 'Mission Completion Checker'
        self.__mission_completion_thread.daemon = True
        self.__mission_completion_thread.start()

    def set_writer(self, writer: DBAdapter = None):
        self.__writer = writer

    def set_controller(self, c):
        self.__controller = c
        
    @property
    def hil_actuator_controls(self):
        return self._hil_actuator_controls

    @property
    def system_time(self):
        return self._system_time

    @property
    def mission_ended(self):
        return self.__mission_ended