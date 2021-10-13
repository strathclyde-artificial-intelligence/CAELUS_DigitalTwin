from abc import abstractmethod, ABC

class Subscriber(ABC):
    @abstractmethod
    def new_datapoint(self, drone_id, stream_id, datapoint):
        pass
    
    @abstractmethod
    def subscribes_to_streams(self):
        return []

    def __repr__(self):
        class_name = str(self.__class__).split('.')[-1][:-2]
        return f'<{class_name}:{[s for s in self.subscribes_to_streams()]}>'