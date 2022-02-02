import logging 
import threading
from queue import Queue
import time
import signal
from .error_codes import *

class OnlyOnMain(Exception):
    pass

class ExitHandler():
    
    __shared_instance = None

    @staticmethod
    def shared():
        if ExitHandler.__shared_instance is None:
            ExitHandler.__shared_instance = ExitHandler()
        return ExitHandler.__shared_instance

    def __init__(self):
        self.__cleanup = {}
        self.__logger = logging.getLogger()
        self.__exit = Queue()

    def register_cleanup_action(self, t, f):
        if t is not None and f is not None:
            self.__cleanup[t.name] = (t, f)
        else:
            self.__logger.warn("Thread and cleanup can't be None.")
        
    def issue_exit_with_code_and_message(self, code, message):
        self.__logger.error(f'Exit issued by {threading.current_thread().name} with code {code}:')
        if message is not None and message != '':
            self.__logger.error(message)
        self.__exit.put_nowait((code, message))
    
    def __run_cleanup_actions(self):
        for t, f in self.__cleanup.values():
            try:
                self.__logger.info(f'Processing cleanup for {t.name}')
                f()
            except Exception as e:
                self.__logger.error(f"Error in processing cleanup for {t.name}")
                if e.__repr__() != '':
                    self.__logger.error(e)
    
    def exit_if_needed(self):
        try:
            code, msg = self.__exit.get_nowait()
            self.__run_cleanup_actions()
            return code, msg
        except Exception as _:
            pass

    def should_exit(self):
        
        if threading.main_thread() != threading.current_thread():
            raise OnlyOnMain("should_exit must be called on the main thread!")

        return not self.__exit.empty()

    def block_until_exit(self):
        signal.signal(signal.SIGINT, lambda _,__: self.issue_exit_with_code_and_message(OK, None))
        self.__logger.info("Entering idle loop for exit handler...")
        while not self.should_exit():
            time.sleep(1)
        self.__logger.info("\n" + "="*30)
        self.__logger.info('Commencing DigitalTwin shutdown!')
        self.__logger.info("="*30 + "\n")
        code, msg = self.exit_if_needed()
        return (code, msg)