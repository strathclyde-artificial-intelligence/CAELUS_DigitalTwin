import threading
import subprocess
import logging
import signal
from time import sleep
from ..Interfaces.Stoppable import Stoppable

class SimulatorWrapper(threading.Thread):

    def __init__(self, simulator_build_folder_location, logger=logging.getLogger(__name__)):
        super().__init__()
        self.name = 'SimulatorWrapper'
        self.__should_stop = False
        self.__sim_folder = simulator_build_folder_location
        self.__process = None
        self.__logger = logger
        self.daemon = False

    def __cleanup(self, timeout = 1):
        self.__logger.info('Cleaning up resources for Simulator Wrapper')
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

    def run(self):
        try:
            self.__process = subprocess.Popen('./6dof',
                cwd=self.__sim_folder,
                shell=True
            )
            while not self.__should_stop and self.__process.poll() is None:
                sleep(1)
        except Exception as e:
            self.__logger.error(e)
        finally:
            self.__cleanup()
            self.__logger.info(f'{__name__} thread terminated')

    def graceful_stop(self):
        self.__should_stop = True

    def halt(self):
        exit(-1)
