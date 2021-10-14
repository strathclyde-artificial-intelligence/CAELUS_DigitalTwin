from abc import ABC, abstractmethod

class Stoppable(ABC):
    
    @abstractmethod
    def graceful_stop(self):
        pass

    @abstractmethod
    def halt(self):
        pass

