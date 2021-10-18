from typing import Tuple, List
from abc import ABC, abstractmethod

class SimulationStack(ABC):

    @abstractmethod
    def restart_stack(self):
        pass