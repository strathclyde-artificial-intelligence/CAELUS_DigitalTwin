from abc import ABC, abstractmethod

class VehicleManager(ABC):
    @abstractmethod
    def vehicle_available(self, vehicle):
        pass
    
    @abstractmethod
    def vehicle_timeout(self, vehicle):
        pass

