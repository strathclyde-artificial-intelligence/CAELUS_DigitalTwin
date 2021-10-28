

from dronekit import Vehicle as DronekitVehicle


class HilActuatorControls(object):
    """
    The message definition is here: https://mavlink.io/en/messages/common.html#HIL_ACTUATOR_CONTROLS
    
    :param time_boot_us: Timestamp (microseconds since system boot).
    :param controls: Control outputs -1 .. 1. Channel assignment depends on the simulated hardware.
    :param mode: System mode. Includes arming state. (https://mavlink.io/en/messages/common.html#MAV_MODE_FLAG)
    :param flags: Flags as bitfield, 1: indicate simulation using lockstep.
    """
    def __init__(self, time_boot_us=None, controls=None, mode=None, flags=None):
        self.time_boot_us = time_boot_us
        self.controls = controls
        self.mode = mode
        self.flags = flags
        
    def __str__(self):
        """
        String representation used to print the RawIMU object. 
        """
        return f"HIL_ACTUATOR_CONTROLS: time_boot_us={self.time_boot_us}, controls={self.controls}"
   
class Vehicle(DronekitVehicle):
    def __init__(self, *args):
        super().__init__(*args)

        # Create an Vehicle.raw_imu object with initial values set to None.
        self._hil_actuator_controls = HilActuatorControls()
        # Create a message listener using the decorator.   
        @self.on_message('HIL_ACTUATOR_CONTROLS')
        def listener(self, name, message):
            self._hil_actuator_controls.time_boot_us=message.time_usec
            self._hil_actuator_controls.controls=message.controls
            self._hil_actuator_controls.mode=message.mode
            self._hil_actuator_controls.flags=message.flags
            self.notify_attribute_listeners('hil_actuator_controls', self._hil_actuator_controls) 


    @property
    def hil_actuator_controls(self):
        return self._hil_actuator_controls