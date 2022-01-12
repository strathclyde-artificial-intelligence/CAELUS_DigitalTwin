import threading
import time

from PySmartSkies.CVMS_API import CVMS_API
from PySmartSkies.DIS_API import DIS_API
from PySmartSkies.DeliveryStatus import *
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

    def __init__(self, vehicle, writer: DBAdapter, controller, mission_items_n, delivery_id = None, smartskies_session = None):
        super().__init__()
        self.__writer = writer
        self.__logger = logging.getLogger()
        self.__vehicle = vehicle
        self.__controller = controller
        self.__mission_items_n = mission_items_n
        self.__cvms_api = CVMS_API(smartskies_session) if smartskies_session is not None else None
        self.__dis_api = DIS_API(smartskies_session) if smartskies_session is not None else None
        self.name = 'Mission Progress Monitor'
        self.__status_steps = {
            0: [STATUS_DELIVERY_REQUESTED,STATUS_DELIVERY_REQUEST_ACCEPTED, STATUS_READY_FOR_DELIVERY],
            4: [STATUS_CLEAR_TO_LAND_CUSTOMER, STATUS_LANDING_CUSTOMER],
        }
        self.__delivery_id = delivery_id
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

    def publish_smartskies_status_update(self, status):
        try:
            if self.__cvms_api is None or self.__dis_api is None:
                self.__logger.warn('Skipping SmartSkies status update -- No API bridge available.')
            elif self.__delivery_id is None:
                self.__logger.warn('No delivery ID provided -- Smartskies update aborted.')
            else:
                if status not in self.__status_steps:
                    return
                items = self.__status_steps[status]
                for i in items:
                    flag = False
                    if i == STATUS_CLEAR_TO_LAND_CUSTOMER: # Must be issued by CVMS
                        flag = self.__cvms_api.provide_clearance_update(self.__delivery_id)
                    else:
                        flag = self.__dis_api.delivery_status_update(self.__delivery_id, i)
                    if flag:
                        self.__logger.info(f'Sent Smartskies Update: {i}')
        except Exception as e:
            import traceback
            self.__logger.error(f'Error in publishing status update (SmartSkies): {e}')
            print(traceback.print_exc())

    def publish_mission_status(self, status):
        if status not in MissionProgressMonitor.mission_status:
            self.__logger.warn("Tried to publish an invalid mission status!")
        self.__logger.info(f'Mission status updated: {self.__mission_status_to_string(status)}')
        self.publish_smartskies_status_update(status)
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