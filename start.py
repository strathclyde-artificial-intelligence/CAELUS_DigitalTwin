from os import environ
from DigitalTwin.CAELUSSimulationStack import CAELUSSimulationStack
from DigitalTwin.DroneController import DroneController
import signal
import atexit 
import logging 
from DigitalTwin.GUI.GUI import GUI
import threading
from os.path import exists

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

def cleanup(gui, sim_stack, signal, frame):
    sim_stack.graceful_stop()
    exit(0)

def check_smartskies_env():
    if not exists('./.env'):
        print(f'.env file contianing SmartSkies credentials not found.')
        print(f'Please create a .env file in the root directory of the digital twin architecture following the format specified in https://github.com/H3xept/CAELUS_SmartSkies')
        exit(-1)

def check_exported_px4():
    if not 'PX4_ROOT_FOLDER' in environ:
        print(f'You must export your local copy of the CAELUS px4 fork folder (export PX4_ROOT_FOLDER=<px4 folder>)')
        exit(-1)

check_exported_px4()
check_smartskies_env()

signal.signal(signal.SIGINT, lambda a,b: cleanup(gui, sstack, a, b))
gui = GUI(init_file=GUI.DEFAULT_GUI_INIT_FILE_NAME)
drone_controller = DroneController()
drone_controller.set_time_series_handler(gui)
sstack = CAELUSSimulationStack(stream_handler=gui)

gui.set_mission_manager(drone_controller)
gui.set_simulation_stack(sstack)

sstack.start()

gui.start()
    
    
# atexit.register(lambda: cleanup(sstack, None, None))