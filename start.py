from dotenv import load_dotenv

from DigitalTwin.PayloadModels import ControllerPayload, SimulatorPayload
load_dotenv()

from os import environ, path
import logging 
from os.path import exists
from DigitalTwin.SimulationFactory import new_simulation

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

def check_smartskies_env():
    if not exists('./.env'):
        logger.error(f'.env file contianing SmartSkies credentials not found.')
        logger.error(f'Please create a .env file in the root directory of the digital twin architecture following the format specified in https://github.com/H3xept/CAELUS_SmartSkies')
        exit(-1)

def check_exported_px4():
    local_px4 = 'Dependencies/PX4-Autopilot'
    if not 'PX4_ROOT_FOLDER' in environ:
        if path.exists(local_px4):
            environ['PX4_ROOT_FOLDER'] = local_px4
        else:
            logger.error(f'You must export your local copy of the CAELUS px4 fork folder (export PX4_ROOT_FOLDER=<px4 folder>)')
            exit(-1)

check_exported_px4()
check_smartskies_env()

config_file = 'example_sim_config.json'
sim_payload = SimulatorPayload.from_json_file(config_file)
controller_payload = ControllerPayload.from_json_file(config_file)
gui, controller, sstack = new_simulation(sim_payload, controller_payload)

sstack.start()
gui.start()