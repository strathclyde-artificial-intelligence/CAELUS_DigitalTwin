from queue import Queue, List
from abc import abstractmethod, ABC

class Producer(ABC):
    
    @abstractmethod
    def get_message_queue_for_stream(self, stream_id) -> Queue:
        raise NotImplementedError()
    
    @abstractmethod
    def produces_to_streams(self) -> List[str]:
        return []

    def __repr__(self):
        class_name = str(self.__class__).split('.')[-1][:-2]
        return f'<Producer: {class_name}>'