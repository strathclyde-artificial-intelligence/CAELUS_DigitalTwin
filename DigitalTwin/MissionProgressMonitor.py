import threading
import time
from .Interfaces.DBAdapter import DBAdapter
import logging
import queue

class MissionProgressMonitor(threading.Thread):

    DB_MISSION_STATUS = 'waypoint_completion'
    TAKING_OFF = 0
    TAKEOFF_COMPLETE = 1
    CRUISING = 2
    LANDING = 3
    LANDING_COMPLETE = 4

    mission_status = [TAKING_OFF, TAKEOFF_COMPLETE, CRUISING, LANDING, LANDING_COMPLETE]

    def __init__(self, vehicle, writer: DBAdapter, controller, mission_items_n):
        super().__init__()
        self.__writer = writer
        self.__logger = logging.getLogger()
        self.__vehicle = vehicle
        self.__controller = controller
        self.__mission_items_n = mission_items_n
        self.name = 'Mission Progress Monitor'
        self.daemon = True
        self.__last_wp = -1

    def __mission_status_to_string(self, s):
        return {
            0: 'Takeoff',
            1: 'Takeoff complete',
            2: 'Cruising',
            3: 'Landing',
            4: 'Landing complete'
        }[s]


    def publish_mission_status(self, status):
        if status not in MissionProgressMonitor.mission_status:
            self.__logger.warn("Tried to publish an invalid mission status!")
        self.__logger.info(f'Mission status updated: {self.__mission_status_to_string(status)}')
        if self.__writer is not None:
            wp_n = max(0, self.__vehicle.commands.next-1) if not (status == MissionProgressMonitor.LANDING_COMPLETE) else self.__mission_items_n
            self.__writer.store({MissionProgressMonitor.DB_MISSION_STATUS:f"{wp_n}/{self.__mission_items_n}"}, series=False)
        if status == MissionProgressMonitor.LANDING_COMPLETE:
            if self.__controller is None:
                self.__logger.warn('Mission complete but no handler to notify!')
            else:
                self.__controller.mission_complete()

    def __process_mission_status(self, waypoint_n):
        if self.__last_wp > 0 and waypoint_n == 0:
            self.publish_mission_status(MissionProgressMonitor.LANDING_COMPLETE)
        elif waypoint_n == 0:
            self.publish_mission_status(MissionProgressMonitor.TAKING_OFF)
        elif waypoint_n == self.__mission_items_n - 1:
            self.publish_mission_status(MissionProgressMonitor.LANDING)
        elif waypoint_n > 0:
            if self.__last_wp == 0:
                self.publish_mission_status(MissionProgressMonitor.TAKEOFF_COMPLETE)
            self.publish_mission_status(MissionProgressMonitor.CRUISING)
        else:
            self.__logger.warn(f'Unrecognised waypoint number: {waypoint_n}')
        self.__last_wp = waypoint_n

    def put_command_in_queue(self, command):
        self.__command_queue.put(command)

    def run(self):
        while True:
            new_waypoint = self.__vehicle.commands.next
            if self.__last_wp != new_waypoint:
                self.__process_mission_status(new_waypoint)
            time.sleep(1)