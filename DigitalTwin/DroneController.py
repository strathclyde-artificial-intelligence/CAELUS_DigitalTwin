from queue import Empty, Queue
import logging
import threading
from ProbeSystem.state_aggregator.state_aggregator import StateAggregator
from typing import Tuple, List
from dataclasses import dataclass

from DigitalTwin.Interfaces.TimeSeriesHandler import TimeSeriesHandler
from DigitalTwin.Probes.ThermalModelProbe import ThermalModelProbe
from .VehicleConnectionManager import VehicleConnectionManager
from .DroneCommander import DroneCommander
from .Interfaces.VehicleManager import VehicleManager
from .Interfaces.MissionManager import MissionManager
from .Interfaces.Stoppable import Stoppable
from .Probes.AnraTelemetryPush import AnraTelemetryPush
from .Probes.TelemetryDisplay import TelemetryDisplay
from .Probes.QuadrotorBatteryDischarge import QuadrotorBatteryDischarge
from .Interfaces.TimeSeriesHandler import TimeSeriesHandler
from .PayloadModels import ControllerPayload

@dataclass
class Mission():
    waypoints: List[Tuple[float, float, float]]
    operation_id: str
    control_area_id: str
    reference_number: str
    drone_registration_number: str
    drone_id: str
    dis_token: str

class DroneController(VehicleManager, MissionManager, Stoppable):
    def __init__(self, controller_payload: ControllerPayload):
        self.__controller_payload = controller_payload
        self.__connection_manager = VehicleConnectionManager(self)
        self.__commander = DroneCommander()
        self.__state_aggregator = StateAggregator(controller_payload.drone_id, should_manage_vehicle=False)
        self.__logger = logging.getLogger(__name__)
        self.__should_stop = False
        self.__mission_queue = Queue()
        self.__mission_poll_thread = None
        self.__state_aggregator_thread = None
        self.__executing_mission = False
        self.__setup_probes()
        self.__connection_manager.connect_to_vehicle()

    def __setup_probes(self):
        self.__logger.info('Setting up probes')
        self.__anra_probe = AnraTelemetryPush()
        self.__telemetry_display_probe = TelemetryDisplay()
        self.__battery_discharge_probe = QuadrotorBatteryDischarge()
        self.__thermal_model_probe = ThermalModelProbe(self.__controller_payload.thermal_model_timestep)
        for probe in [
            self.__anra_probe,
            self.__telemetry_display_probe,
            self.__battery_discharge_probe,
            self.__thermal_model_probe
        ]:
            for stream_id in probe.subscribes_to_streams():
                self.__state_aggregator.subscribe(stream_id, probe)
        self.__state_aggregator.report_subscribers()
        
    def vehicle_available(self, vehicle):
        self.__logger.info(f'New vehicle available {vehicle}')
        self.__commander.set_vehicle(vehicle)
        
        self.__state_aggregator.set_vehicle(vehicle)
        self.__state_aggregator_thread = threading.Thread(target=self.__state_aggregator.idle, args=())
        self.__state_aggregator_thread.name = 'StateAggregator Main-Thread'
        self.__state_aggregator_thread.daemon = True
        self.__state_aggregator_thread.start()

        self.__battery_discharge_probe.set_vehicle(vehicle)
        
        self.mission_poll_thread_start()
        self.__load_mission_from_payload()

    def __load_mission_from_payload(self):
        self.__logger.info(f'Loading mission from configuration payload')
        self.add_mission(Mission(
            self.__controller_payload.waypoints,
            self.__controller_payload.operation_id,
            self.__controller_payload.control_area_id,
            self.__controller_payload.operation_reference_number,
            self.__controller_payload.drone_id,
            self.__controller_payload.drone_registration_number,
            self.__controller_payload.dis_auth_token
        ))

    def vehicle_timeout(self, vehicle):
        self.__logger.info(f'Vehicle timed out!')
        self.__should_stop = True
        self.__connection_manager.stop_connecting()
        self.__connection_manager.connect_to_vehicle()

    def poll_mission(self):
        while not self.__should_stop:
            if not self.__executing_mission:
                try:
                    mission: Mission = self.__mission_queue.get(block=False)
                    waypoints_alt = mission.waypoints
                    self.__executing_mission = True
                    waypoints, alt = [[a[0], a[1]] for a in waypoints_alt], waypoints_alt[0][-1]

                    self.__logger.info('Received new mission')
                    self.__commander.set_mission(waypoints, altitude=alt)
                    self.__commander.start_mission()

                    self.__anra_probe.start_sending_telemetry(
                        drone_registration=mission.drone_registration_number,
                        operation_id=mission.operation_id,
                        control_area_id=mission.control_area_id,
                        reference_number=mission.reference_number,
                        dis_token=mission.dis_token
                    )

                except Empty as e:
                    pass
                except Exception as e:
                    self.__logger.warn(e)
        self.__logger.info('Mission poll thread complete.')

    def mission_poll_thread_start(self):
        try:
            self.__logger.info('Mission poll thread start.')
            self.__mission_poll_thread = threading.Thread(target=self.poll_mission)
            self.__mission_poll_thread.name = 'Mission Poll'
            self.__mission_poll_thread.daemon = True
            self.__mission_poll_thread.start()
        except Exception as e:
            self.__logger.warn(e) 

    def add_mission(self, mission: Mission):
        self.__logger.info(f'Received new mission! Enqueueing...')
        self.__mission_queue.put(mission)

    def graceful_stop(self):
        self.__connection_manager.stop_connecting()
        self.__should_stop = True

    def halt(self):
        exit(-1)

    def set_time_series_handler(self, ts_handler: TimeSeriesHandler):
        assert ts_handler is not None
        self.__telemetry_display_probe.set_time_series_handler(ts_handler)