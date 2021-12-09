import threading
import subprocess
import logging
import signal
from time import sleep
from typing import Optional
from ..Interfaces.Stoppable import Stoppable
from ..Interfaces.StreamHandler import StreamHandler
from ..PayloadModels import SimulatorPayload

class JMAVSimWrapper(threading.Thread):

    def __init__(self, simulator_jar_file_location, initial_lon_lat_alt, simulator_payload: SimulatorPayload, stream_handler: Optional[StreamHandler] = None, logger=logging.getLogger(__name__)):
        super().__init__()
        self.name = 'JMAVSimWrapper'
        self.__simulator_payload: SimulatorPayload = simulator_payload
        self.__initial_lon_lat_alt = initial_lon_lat_alt
        self.__should_stop = False
        self.__sim_folder = simulator_jar_file_location
        self.__process = None
        self.__logger = logger
        self.__stream_handler = stream_handler
        self.__streams = set()
        # Wait for this lock to properly destroy this wrapper
        self.termination_complete = threading.Condition()
        self.daemon = False

    def __cleanup(self, timeout = 1):
        self.__logger.info('Cleaning up resources for Simulator Wrapper')
        
        self.__logger.info(f'Invalidating streams for {__name__}')
        for s in self.__streams:
            self.__invalidate_stream(s)
        self.__streams = []

        self.__logger.info(f'Waiting for Simulator process to exit...')
        if self.__process is not None:
            for t in range(timeout):
                code = self.__process.poll()
                if code is not None:
                    self.__logger.info(f'Process spontaneously exited with code {code}.')
                    return code
                sleep(t)
            self.__logger.info(f'Poll timeout expired, killing {self.__process}')    
            self.__process.kill()

    def __new_stream_available(self, stream_name, stream):
        if self.__stream_handler is not None:
            self.__streams.add(stream_name)
            self.__stream_handler.new_stream_available(stream_name, stream)

    def __invalidate_stream(self, stream_name):
        if self.__stream_handler is not None:
            self.__stream_handler.invalidate_stream(stream_name)

    def run(self):
        self.termination_complete.acquire()
        try:
            lon, lat, alt = self.__initial_lon_lat_alt
            drone_conf = self.__simulator_payload.drone_config
            self.__process = subprocess.Popen(
                'export PX4_SIM_SPEED_FACTOR=10; '
                f'export PX4_HOME_LAT={lat};'
                f'export PX4_HOME_LON={lon};'
                f'export PX4_HOME_ALT={alt};'
                f'java -XX:GCTimeRatio=20 -Djava.ext.dirs= -jar jmavsim_run.jar -tcp 127.0.0.1:4560 -r 250 -lockstep -no-gui -drone-config "{drone_conf}"',
                cwd=self.__sim_folder,
                shell=True,
                stdout=subprocess.PIPE
            )
            self.__new_stream_available('sim_stdout', self.__process.stdout)
            while not self.__should_stop and self.__process.poll() is None:
                sleep(1)
        except Exception as e:
            self.__logger.error(e)
        finally:
            self.__cleanup()
            self.__logger.info(f'{__name__} thread terminated')
            self.termination_complete.release()

    def graceful_stop(self):
        self.__should_stop = True
        self.__process.send_signal(signal.SIGINT)

    def halt(self):
        exit(-1)
