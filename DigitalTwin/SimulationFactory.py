from DigitalTwin.CAELUSSimulationStack import CAELUSSimulationStack
from DigitalTwin.DroneController import DroneController
from .PayloadModels import *
import signal
from .MongoDBWriter import MongoDBWriter
from .WeatherDataProvider import WeatherDataProvider

def cleanup(gui, sim_stack, signal, frame, weather_provider):
    sim_stack.graceful_stop()
    weather_provider.close()
    exit(0)

def get_writer(operation_id, group_id):
    try:
        client = MongoDBWriter.acquire_client()
        return MongoDBWriter(client, operation_id, group_id)
    except TimeoutError:
        print('Could not connect to database (MongoDB) -- aborting')
        exit(-1)

def new_simulation(simulator_payload: SimulatorPayload, controller_payload: ControllerPayload, headless=False):
    if not headless:
        from DigitalTwin.GUI.GUI import GUI
    
    writer = get_writer(controller_payload.operation_id, controller_payload.group_id)
    writer.start()

    weather_provider = WeatherDataProvider(controller_payload)
    weather_provider.prepare_weather_data()

    gui = GUI(init_file=GUI.DEFAULT_GUI_INIT_FILE_NAME) if not headless else None
    drone_controller = DroneController(controller_payload, weather_provider, writer)
    drone_controller.set_time_series_handler(gui)

    sstack = CAELUSSimulationStack(simulator_payload, stream_handler=gui, weather_provider=weather_provider)
    if gui is not None:
        gui.set_mission_manager(drone_controller)
        gui.set_simulation_stack(sstack)

    signal.signal(signal.SIGINT, lambda a,b: cleanup(gui, sstack, a, b, weather_provider))
    
    return gui, drone_controller, sstack
