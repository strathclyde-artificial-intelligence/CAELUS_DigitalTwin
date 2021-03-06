import threading
import subprocess
import logging
import signal
from time import sleep
from typing import Optional
from ..Interfaces.Stoppable import Stoppable
from ..Interfaces.StreamHandler import StreamHandler

class SimulatorWrapper(threading.Thread):

    def __init__(self, simulator_build_folder_location, stream_handler: Optional[StreamHandler] = None, logger=logging.getLogger(__name__)):
        super().__init__()
        self.name = 'SimulatorWrapper'
        self.__should_stop = False
        self.__sim_folder = simulator_build_folder_location
        self.__process = None
        self.__logger = logger
        self.__stream_handler = stream_handler
        self.__streams = set()
        # Wait for this lock to properly destroy this wrapper
        self.termination_complete = threading.Condition()
        self.daemon = False

    def __cleanup(self):
        self.__logger.info('Cleaning up resources for Simulator Wrapper')
        
        self.__logger.info(f'Invalidating streams for {__name__}')
        for s in self.__streams:
            self.__invalidate_stream(s)
        self.__streams = []

        self.__logger.info(f'Waiting for Simulator process to exit...')
        if self.__process is not None:
            for t in range(1):
                code = self.__process.poll()
                if code is not None:
                    self.__logger.info(f'Process spontaneously exited with code {code}.')
                    return code
                sleep(t)
            self.__logger.info(f'Poll timeout expired, killing {self.__process}')    
            self.__process.kill()

    def __new_stream_available(self, stream_name, stream):
        self.__streams.add(stream_name)
        self.__stream_handler.new_stream_available(stream_name, stream)

    def __invalidate_stream(self, stream_name):
        self.__stream_handler.invalidate_stream(stream_name)

    def run(self):
        self.termination_complete.acquire()
        try:
            self.__process = subprocess.Popen('./6dof',
                cwd=self.__sim_folder,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
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

    def halt(self):
        exit(-1)
