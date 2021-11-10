import asyncio
from queue import Queue
from threading import Thread, Condition
import threading
from typing import NewType, Dict, Tuple, List

from .simulation_bridge import SimulationBridge
from ..helper_data.subscriber import Subscriber
from ..helper_data.producer import Producer

DataPoint = NewType('DataPoint', Tuple[object, str])

META_MESSAGE_N = 'message_n'

class StateAggregator():
    def __init__(self, drone_instance_id, should_manage_vehicle = True):
        
        self.streams: Dict[str, DataPoint] = {}
        self.stream_metadata: Dict[str, Dict[str, object]] = {}
        self.subscribers: Dict[str, List[Subscriber]] = {}
        self.producer_queues: Dict[str, List[Queue]] = {}
        self.__should_manage_vehicle = should_manage_vehicle
        self.drone_instance_id = drone_instance_id
        self.should_shutdown = Condition()
        self.simulation_bridge = SimulationBridge(self, self.should_shutdown, should_manage_vehicle)
        self.bridge_thread = self.__setup_bridge()
        self.__setup_producer_fetch_thread()

    def __setup_producer_fetch_thread(self):
        self.__producer_fetch_thread = threading.Thread(target=self.producer_fetch_thread)
        self.__producer_fetch_thread.daemon = True
        self.__producer_fetch_thread.name = 'Producer fetch thread'
        self.__producer_fetch_thread.start()

    def __setup_bridge(self):
        if self.__should_manage_vehicle:
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
        return None

    # Periodically check producer queues and dispatch new events if present
    def producer_fetch_thread(self):
        try:
            while True:
                for s, qs in self.producer_queues.items():
                    for q in qs:
                        if q.empty():
                            continue
                        self.new_datapoint_for_stream(s, q.get())
        except Exception as e:
            print("THIS SHOULD NEVER HAPPEN")
            raise e

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

    def add_producer(self, producer: Producer):
        for s in producer.produces_to_streams():
            if s not in self.producer_queues:
                self.producer_queues[s] = []
            self.producer_queues[s].append(producer.get_message_queue_for_stream(s))

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
        for stream_id, subs in self.subscribers.items():
            print(f'[STREAM] "{stream_id}" has {len(subs)} {"subscribers" if len(subs) > 1 else "subscriber"}')
            if stream_id not in available_streams:
                print('[WARNING] This stream is not published by the state aggregator!')
            for sub in subs:
                print(f'\t{sub}')

    def report_producers(self):
        print('Producer queues:')
        for stream, qs in self.producer_queues.items():
            print(f'{stream} has {len(qs)} producers.')

    def idle(self):
        self.should_shutdown.acquire()
        self.should_shutdown.wait()

    # To be called from a third party when the probe system does not manage the vehicle connection
    def set_vehicle(self, vehicle):
        self.simulation_bridge.vehicle_acquired(None, vehicle)