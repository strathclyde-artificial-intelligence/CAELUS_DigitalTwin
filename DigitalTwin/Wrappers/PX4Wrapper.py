import threading
import subprocess
import logging
import signal
from typing import Optional
from time import sleep
from ..Interfaces.Stoppable import Stoppable
from ..Interfaces.StreamHandler import StreamHandler

class PX4Wrapper(threading.Thread):

    def __init__(self, px4_root_folder_location, stream_handler: Optional[StreamHandler] = None, logger=logging.getLogger(__name__)):
        super().__init__()
        self.name = 'PX4Wrapper'
        self.__should_stop = False
        self.__px4_folder = px4_root_folder_location
        self.__process = None
        self.__logger = logger
        self.__stream_handler = stream_handler
        self.__streams = []
        self.daemon = False

    def __new_stream_available(self, stream_name, stream):
        self.__streams.append(stream_name)
        self.__stream_handler.new_stream_available(stream_name, stream)

    def __invalidate_stream(self, stream_name):
        self.__streams.remove(stream_name)
        self.__stream_handler.invalidate_stream(stream_name)

    def __cleanup(self, timeout = 1):
        self.__logger.info('Cleaning up resources for PX4 Wrapper')
        
        self.__logger.info(f'Invalidating streams for {__name__}')
        for s in self.__streams:
            self.__invalidate_stream(s)

        self.__logger.info(f'Waiting for PX4 process to exit...')
        
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
            self.__process = subprocess.Popen('make px4_sitl none_custom_quad',
                cwd=self.__px4_folder,
                shell=True,
                stdout=subprocess.PIPE
            )
            self.__new_stream_available('px4_stdout', self.__process.stdout)
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
