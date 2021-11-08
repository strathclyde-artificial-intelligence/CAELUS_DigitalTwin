import os
import logging
import dearpygui.dearpygui as dpg
from ..Interfaces.SimulationStack import SimulationStack
from ..Interfaces.MissionManager import MissionManager
from .MissionHelper import MissionHelper
from ..DroneController import Mission

class MissionWindow():
    def __init__(self, dpg):
        super().__init__()
        self.__dpg: dpg = dpg
        self.__mission_helper = MissionHelper(os.environ)
        self.__sim_stack: SimulationStack = None
        self.__mission_manager: MissionManager = None
        self.__logger = logging.getLogger(__name__)
        self.setup_window()

    def setup_window(self):
        self.mission_window = 'MissionWindow'

        with self.__dpg.window(label=self.mission_window, tag=self.mission_window):
            self.__dpg.add_button(label='Restart Simulation', callback=self.restart_stack)
            self.__dpg.add_button(label='Execute Example Mission', callback=self.execute_sample_mission)

    def restart_stack(self):
        if self.__sim_stack is not None:
            self.__sim_stack.restart_stack()
        else:
            self.__logger.warn('No simulation stack setup (GUI)!')

    def set_sim_stack(self, sim_stack):
        self.__logger.info(f'Mission Window received simulation stack {sim_stack}')
        self.__sim_stack = sim_stack

    def set_mission_manager(self, mission_manager):
        self.__logger.info(f'Mission Window received mission manager {mission_manager}')
        self.__mission_manager = mission_manager

    def execute_sample_mission(self):
        operation, operation_id, drone, dis_token = self.__mission_helper.example_mission_waypoints()
        self.__mission_manager.add_mission(Mission(
            operation.get_waypoints(),
            operation_id,
            operation.control_area_id,
            operation.reference_number,
            drone,
            dis_token
        ))

    def update(self):
        pass
    