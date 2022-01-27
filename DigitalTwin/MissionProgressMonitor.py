import threading
import time
from tkinter import EXCEPTION

from PySmartSkies.CVMS_API import CVMS_API
from dronekit import VehicleMode
from PySmartSkies.DIS_API import DIS_API
from PySmartSkies.DeliveryStatus import *
from .Interfaces.DBAdapter import DBAdapter
import logging
import queue
from time import sleep

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
            3: [STATUS_READY_FOR_LANDING_CUSTOMER, STATUS_CLEAR_TO_LAND_CUSTOMER, STATUS_LANDING_CUSTOMER, STATUS_READY_FOR_PACKAGE_PICKUP, STATUS_PACKAGE_DELIVERED]
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

    def __wait_for_clear_to_land(self):
        CLEAR_TO_LAND_CODE = 14
        EXCEPT_CODES = [19, 22]
        def __wait():
            try:
                while True:
                    status = self.__dis_api.get_delivery_status_id(self.__delivery_id)
                    if status >= CLEAR_TO_LAND_CODE and status not in EXCEPT_CODES:
                        self.__logger.info("Received clear to land signal - Initiating land")
                        break
                    print(status)
                    sleep(2)
            except Exception as e:
                self.__logger.error(f'Errored while waiting for clear to land signal')
                self.__logger.error(e)
        previous_mode = self.__vehicle.mode
        self.__logger.info('Setting vehicle to loiter')
        self.__vehicle.mode = VehicleMode("LOITER")
        t = threading.Thread(target=__wait)
        t.name = "Landing clearance update"
        self.__logger.info('Waiting for clear to land signal from SmartSkies')
        self.__logger.info('Customer sending clear to land signal')
        self.__cvms_api.provide_clearance_update(self.__delivery_id)
        t.start()
        t.join()
        self.__logger.info('Drone allowed to land.')
        self.__vehicle.mode = previous_mode
                
    def __drone_ready_for_landing(self):
        if self.__dis_api is None:
            self.__logger.warn('Controller skipped ready to land signal because no SmartSkies API is available.')
            return
        self.__wait_for_clear_to_land()

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
                self.__logger.info(f'About to publish updates: {items}')
                for i in items:
                    flag = False
                    self.__logger.info(f'Sending {i}')
                    if i == STATUS_CLEAR_TO_LAND_CUSTOMER:
                        flag = self.__dis_api.delivery_status_update(self.__delivery_id, i)
                    else:
                        flag = self.__dis_api.delivery_status_update(self.__delivery_id, i)
                    if flag:
                        self.__logger.info(f'Sent Smartskies Update: {i}')
                    time.sleep(1)
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
                self.__logger.info("Controller notified of mission completion.")
                self.__controller.mission_complete()

    def __process_mission_status(self, waypoint_n):
        if (self.__last_wp > 0 and waypoint_n == 0) and not self.__vehicle.armed:
            self.close_delivery_operation()
            self.publish_mission_status(MissionProgressMonitor.LANDING_COMPLETE)
        elif waypoint_n == 0:
            self.publish_mission_status(MissionProgressMonitor.TAKING_OFF)
        elif waypoint_n == self.__mission_items_n - 2:
            self.__drone_ready_for_landing()
            self.publish_mission_status(MissionProgressMonitor.LANDING)
        elif waypoint_n > 0:
            if self.__last_wp == 0:
                self.publish_mission_status(MissionProgressMonitor.TAKEOFF_COMPLETE)
            self.publish_mission_status(MissionProgressMonitor.CRUISING)
        else:
            self.__logger.warn(f'Unrecognised waypoint number: {waypoint_n}')
        self.__last_wp = waypoint_n

    def close_delivery_operation(self):
        # Mission must be aborted as there's no return leg for now
        self.__dis_api.abort_delivery(self.__delivery_id)
        self.__logger.info(f'Sending delivery end notification to SmartSkies (id: {self.__delivery_id})')
        self.__dis_api.end_or_close_delivery(self.__delivery_id)

    def put_command_in_queue(self, command):
        self.__command_queue.put(command)

    def run(self):
        try:
            while True:
                new_waypoint = self.__vehicle.commands.next
                if self.__last_wp != new_waypoint:
                    self.__process_mission_status(new_waypoint)
                time.sleep(1)

        except Exception as e:
            self.__logger.error('Error in main loop (Mission progress monitor):')
            self.__logger.error(e)