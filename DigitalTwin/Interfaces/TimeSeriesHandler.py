from abc import ABC, abstractmethod

class TimeSeriesHandler(ABC):
    @abstractmethod
    def new_time_series_stream_available(self, name, stream):
        pass
    
        