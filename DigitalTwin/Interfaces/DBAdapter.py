from abc import ABC, abstractmethod

class DBAdapter(ABC):
    @abstractmethod
    def store(self, data, series=True):
        raise NotImplementedError