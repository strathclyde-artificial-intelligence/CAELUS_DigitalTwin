# https://dronekit-python.readthedocs.io/en/latest/automodule.html#dronekit.Vehicle.gps_0

# Location in global frame (a LocationGlobal).
# The latitude and longitude are relative to the WGS84 coordinate system.
# The altitude is relative to mean sea-level (MSL).
GLOBAL_FRAME = 'location.global_frame'

# Location in global frame, with altitude relative to the home location (a LocationGlobalRelative).
# The latitude and longitude are relative to the WGS84 coordinate system.
# # The altitude is relative to home location.
GLOBAL_RELATIVE_FRAME = 'location.global_relative_frame'

# Location in local NED frame (a LocationGlobalRelative).
# This location will not start to update until the vehicle is armed.
LOCAL_FRAME = 'location.local_frame'

# Current vehicle attitude - pitch, yaw, roll (Attitude).
ATTITUDE = 'attitude'

# Current velocity as a three element list [ vx, vy, vz ] (in meter/sec).
VELOCITY = 'velocity'

# Standard information about GPS.
# If there is no GPS lock the parameters are set to None.
# Parameters:	
# eph (Int) – GPS horizontal dilution of position (HDOP).
# epv (Int) – GPS vertical dilution of position (VDOP).
# fix_type (Int) – 0-1: no fix, 2: 2D fix, 3: 3D fix
# satellites_visible (Int) – Number of satellites visible.
GPS = 'gps_0'

# System battery information.
# An object of this type is returned by Vehicle.battery.
# Parameters:	
# voltage – Battery voltage in millivolts.
# current – Battery current, in 10 * milliamperes. None if the autopilot does not support current measurement.
# level – Remaining battery energy. None if the autopilot cannot estimate the remaining battery.
BATTERY = 'battery'

# True if the EKF status is considered acceptable, False otherwise (boolean).
EKF_OK = 'ekf_ok'

# System status (SystemStatus).
# The status has a state property with one of the following values:
# UNINIT: Uninitialized system, state is unknown.
# BOOT: System is booting up.
# CALIBRATING: System is calibrating and not flight-ready.
# STANDBY: System is grounded and on standby. It can be launched any time.
# ACTIVE: System is active and might be already airborne. Motors are engaged.
# CRITICAL: System is in a non-normal flight mode. It can however still navigate.
# EMERGENCY: System is in a non-normal flight mode. It lost control over parts or over the whole airframe. It is in mayday and going down.
# POWEROFF: System just initialized its power-down sequence, will shut down now.
SYSTEM_STATUS = 'system_status'

# Current heading in degrees - 0..360, where North = 0 (int).
HEADING = 'heading'

# Returns True if the vehicle is ready to arm, false otherwise (Boolean).
# This attribute wraps a number of pre-arm checks, ensuring that the vehicle has booted, has a good GPS fix, and that the EKF pre-arm is complete.
IS_ARMABLE = 'is_armable'

# Time since last MAVLink heartbeat was received (in seconds).
# The attribute can be used to monitor link activity and implement script-specific timeout handling.
LAST_HEARTBEAT = 'last_heartbeat'

# Current airspeed in metres/second (double).
AIRSPEED = 'airspeed'

# Current groundspeed in metres/second (double).
GROUND_SPEED = 'groundspeed'

# Current vehicle mode.
VEHICLE_MODE = 'mode.name'

# Armed state of the vehicle.
ARMED = 'armed'
