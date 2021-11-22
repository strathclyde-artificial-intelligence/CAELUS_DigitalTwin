from DigitalTwin.CAELUSSimulationStack import CAELUSSimulationStack
from DigitalTwin.DroneController import DroneController
from .PayloadModels import *
import signal

def cleanup(gui, sim_stack, signal, frame):
    sim_stack.graceful_stop()
    exit(0)

def new_simulation(simulator_payload: SimulatorPayload, controller_payload: ControllerPayload, headless=False):
    if not headless:
        from DigitalTwin.GUI.GUI import GUI
    gui = GUI(init_file=GUI.DEFAULT_GUI_INIT_FILE_NAME) if not headless else None
    drone_controller = DroneController(controller_payload)
    drone_controller.set_time_series_handler(gui)
    sstack = CAELUSSimulationStack(simulator_payload, stream_handler=gui)
    if gui is not None:
        gui.set_mission_manager(drone_controller)
        gui.set_simulation_stack(sstack)
    signal.signal(signal.SIGINT, lambda a,b: cleanup(gui, sstack, a, b))
    
    return gui, drone_controller, sstack
