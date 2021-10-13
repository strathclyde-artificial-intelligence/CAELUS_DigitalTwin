import asyncio
from threading import Thread, Condition
from typing import NewType, Dict, Tuple

from .simulation_bridge import SimulationBridge
from ..helper_data.subscriber import Subscriber

DataPoint = NewType('DataPoint', Tuple[object, str])

META_MESSAGE_N = 'message_n'

class StateAggregator():
    def __init__(self, drone_instance_id):
        
        self.streams: Dict[str, DataPoint] = {}
        self.stream_metadata: Dict[str, Dict[str, object]] = {}
        self.subscribers: Dict[str, List[Subscriber]] = {}

        self.drone_instance_id = drone_instance_id
        self.should_shutdown = Condition()
        self.simulation_bridge = SimulationBridge(self, self.should_shutdown)
        self.bridge_thread = self.__setup_bridge()

    def __setup_bridge(self):
        # The bridge needs to acquire a connection with the drone
        # hence I'm setting up a lock to notify the connected state
        # and continue with the context initialisation 
        done_setting_up = Condition()
        thread = Thread(target=self.simulation_bridge.initialise, args=(done_setting_up,))
        thread.start()

        done_setting_up.acquire()
        done_setting_up.wait()
        done_setting_up.release()

        return thread

    def __increase_message_count(self, stream_id):
        if META_MESSAGE_N not in self.stream_metadata[stream_id]:
            self.stream_metadata[stream_id][META_MESSAGE_N] = 0
        self.stream_metadata[stream_id][META_MESSAGE_N] += 1

    def __aggregate_datapoint_metadata(self, stream_id, datapoint):
        if stream_id not in self.stream_metadata:
            self.stream_metadata[stream_id] = {}
        self.__increase_message_count(stream_id)

    def __publish_new_datapoint(self, stream_id, datapoint):
        if stream_id not in self.subscribers:
            return
        for sub in self.subscribers[stream_id]:
            sub.new_datapoint('test_id', stream_id, datapoint)

    def __process_raw_datapoint(self, stream_id: str, datapoint: DataPoint):
        self.streams[stream_id] = datapoint
        self.__publish_new_datapoint(stream_id, datapoint)

    def new_datapoint_for_stream(self, stream_id: str, datapoint: DataPoint):
        self.__process_raw_datapoint(stream_id, datapoint)
        self.__aggregate_datapoint_metadata(stream_id, datapoint)

    def subscribe(self, stream_id, subscriber):
        if stream_id not in self.simulation_bridge.get_available_streams():
            print(f'[WARNING] The requested stream is not available ({stream_id})')
        if stream_id not in self.subscribers:
            self.subscribers[stream_id] = []
        self.subscribers[stream_id].append(subscriber)

    def unsubscribe(self, stream_id, subscriber):
        if stream_id not in self.subscribers[stream_id]:
            print('[WARNING] Tried to remove a subscriber from a probe without subscribers.')
            return
        index = self.subscribers[stream_id].find(subscriber)
        if index == -1:
            print(f'[WARNING] The object {subscriber} is not subscribed to the stream "{stream_id}"')
        self.subscribers[stream_id].remove(subscriber)

    def report_subscribers(self):
        available_streams = self.simulation_bridge.get_available_streams()
        print(self.subscribers)
        for stream_id, subs in self.subscribers.items():
            print(f'[STREAM] "{stream_id}" has {len(subs)} {"subscribers" if len(subs) > 1 else "subscriber"}')
            if stream_id not in available_streams:
                print('[WARNING] This stream is not published by the state aggregator!')
            for sub in subs:
                print(f'\t{sub}')

    def idle(self):
        self.should_shutdown.acquire()
        self.should_shutdown.wait()