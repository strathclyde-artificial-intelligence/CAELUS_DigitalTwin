from typing import Tuple, List
from abc import ABC, abstractmethod

class MissionManager(ABC):

    @abstractmethod
    def add_mission(self, mission: Tuple[List[float], float]):
        pass