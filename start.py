from DigitalTwin.CAELUSSimulationStack import CAELUSSimulationStack
from DigitalTwin.DroneController import DroneController
import signal
import atexit 
import logging 
from DigitalTwin.GUI.GUI import GUI
import threading

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

def cleanup(gui, sim_stack, signal, frame):
    sim_stack.graceful_stop()
    exit(0)

signal.signal(signal.SIGINT, lambda a,b: cleanup(gui, sstack, a, b))
gui = GUI(init_file=GUI.DEFAULT_GUI_INIT_FILE_NAME)
drone_controller = DroneController()
sstack = CAELUSSimulationStack(stream_handler=gui)
gui.set_mission_manager(drone_controller)
gui.set_simulation_stack(sstack)
sstack.start()
gui.start()
    
    
# atexit.register(lambda: cleanup(sstack, None, None))