from queue import Queue
from threading import Thread, get_ident
from abc import abstractmethod, ABC
import threading

class Subscriber(ABC, Thread):

    def __init__(self) -> None:
        super().__init__()
        self.daemon = True
        self.name = f'PROBE_{self}'
        self.__setup_queue()
        
    def run(self) -> None:
        q: Queue = self.queue
        while True:
            data = q.get(block=True)
            self.new_datapoint(*data)

    def __setup_queue(self):
        self.queue = Queue()

    def add_to_queue(self, drone_id, stream_id, datapoint):
        self.queue.put_nowait((drone_id, stream_id, datapoint))

    @abstractmethod
    def new_datapoint(self, drone_id, stream_id, datapoint):
        pass
    
    @abstractmethod
    def subscribes_to_streams(self):
        return []

    def __repr__(self):
        class_name = str(self.__class__).split('.')[-1][:-2]
        return f'<{class_name}:{[s for s in self.subscribes_to_streams()]}>'