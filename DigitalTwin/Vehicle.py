import logging
from dronekit import Vehicle as DronekitVehicle
from threading import Thread
import time
from PySmartSkies.DIS_API import DIS_API
from PySmartSkies.CVMS_API import CVMS_API
from PySmartSkies.Session import Session

from DigitalTwin.Interfaces.DBAdapter import DBAdapter
from DigitalTwin.MissionProgressMonitor import MissionProgressMonitor

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

    def __init__(self, *args):
        super().__init__(*args)
        
        self.__logger = logging.getLogger()
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

    def prepare_for_mission(self, mission_items_n):

        self.__logger.info(f"Preparing for mission with {mission_items_n} items")
        
        self.__mission_completion_thread = MissionProgressMonitor(self, self.__writer, self.__controller, mission_items_n, self.__delivery_id, self.__smartskies_session)
        self.__mission_completion_thread.start()

    def set_writer(self, writer: DBAdapter = None):
        self.__writer = writer

    def set_controller(self, c):
        self.__controller = c
    
    def set_smartskies_auth_data(self, dis_token, dis_refresh_token, cvms_token, delivery_id):
        self.__smartskies_session = Session.with_tokens(dis_token, dis_refresh_token, cvms_token)
        self.__delivery_id = delivery_id

    @property
    def hil_actuator_controls(self):
        return self._hil_actuator_controls

    @property
    def system_time(self):
        return self._system_time
