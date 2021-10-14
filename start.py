from DigitalTwin.SimulationStack import SimulationStack
import signal
import atexit 
import logging 
from DigitalTwin.GUI.GUI import GUI

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

def cleanup(gui, sim_stack, signal, frame):
    sim_stack.graceful_stop()
    exit(0)

signal.signal(signal.SIGINT, lambda a,b: cleanup(gui, sstack, a, b))
gui = GUI()
sstack = SimulationStack(stream_handler=gui)
sstack.start()
gui.start()
    
    
# atexit.register(lambda: cleanup(sstack, None, None))