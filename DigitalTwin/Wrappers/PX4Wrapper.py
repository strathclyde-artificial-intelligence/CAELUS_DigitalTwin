from sys import stdin
import threading
import subprocess
import logging
import signal
from typing import Optional
from time import sleep
from ..Interfaces.Stoppable import Stoppable
from ..Interfaces.StreamHandler import StreamHandler
from threading import Thread
from ..error_codes import *

class PX4Wrapper(threading.Thread):

    def __init__(self, px4_root_folder_location, initial_lon_lat_alt, airframe_id: str, stream_handler: Optional[StreamHandler] = None, logger=logging.getLogger(__name__)):
        super().__init__()
        self.name = 'PX4Wrapper'
        self.__should_stop = False
        self.__initial_lon_lat_alt = initial_lon_lat_alt
        self.__px4_folder = px4_root_folder_location
        self.__process = None
        self.__logger = logger
        self.__stream_handler = stream_handler
        self.termination_complete = threading.Condition()
        self.__streams = set()
        self.__airframe_id = airframe_id
        self.daemon = False

    def __new_stream_available(self, stream_name, stream):
        if self.__stream_handler is not None:
            self.__streams.add(stream_name)
            self.__stream_handler.new_stream_available(stream_name, stream)

    def __invalidate_stream(self, stream_name):
        if self.__stream_handler is not None:
            self.__stream_handler.invalidate_stream(stream_name)

    def __cleanup(self):
        self.__logger.info('Cleaning up resources for PX4 Wrapper')
        
        self.__logger.info(f'Invalidating streams for {__name__}')
        for s in self.__streams:
            self.__invalidate_stream(s)
        self.__streams = []

        self.__logger.info(f'Waiting for PX4 process to exit...')
        if self.__process is not None:
            self.__process.kill()
    
    # To be run on a separate thread 
    def monitor_px4_output(self, stream):
        triggers = {
            'IGN MISSION_ITEM': MISSION_UPLOAD_FAIL,
            'Operation timeout': MISSION_UPLOAD_FAIL,
            'poll timeout': PX4_SIM_DESYNC
        }
        t_keys = triggers.keys()
        if stream is None:
            exit(STREAM_READ_FAILURE)
        while not self.__should_stop and stream.readable():
            line = stream.readline().decode('utf-8')
            for k in t_keys:
                if k in line:
                    exit(triggers[k])

    def run(self):
        self.termination_complete.acquire()
        try:
            self.__process = subprocess.Popen(
                f'make px4_sitl none_{self.__airframe_id}', 
                shell=True,
                cwd=self.__px4_folder,
                stdout=subprocess.PIPE, # if self.__stream_handler is not None else None,
                stderr=subprocess.STDOUT
            )
            output_monitor = Thread(target=self.monitor_px4_output, args=(self.__process.stdout,))
            output_monitor.name = 'PX4 Output Monitor'
            output_monitor.daemon = True
            output_monitor.start()

            self.__new_stream_available('px4_stdout', self.__process.stdout)
            while not self.__should_stop and self.__process.poll() is None:
                sleep(1)
            self.__logger.info('PX4 Thread is exiting!')
        except Exception as e:
            self.__logger.error(e)
        finally:
            self.__cleanup()
            self.__logger.info(f'{__name__} thread terminated')
            self.termination_complete.release()

    def graceful_stop(self):
        self.__logger.info('PX4 asked to gracefully stop...')
        self.__should_stop = True  

    def halt(self):
        exit(-1)
