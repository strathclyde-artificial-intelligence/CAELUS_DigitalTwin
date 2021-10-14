from abc import ABC, abstractmethod

class StreamHandler(ABC):
    @abstractmethod
    def new_stream_available(self, stream_name, stream):
        pass
    
    @abstractmethod
    def invalidate_stream(self, stream_name):
        pass
        