import logging
from .Interfaces.DBAdapter import DBAdapter
from pymongo import MongoClient
from threading import Thread
from queue import Queue
import time
from os import environ

class MongoDBWriter(Thread, DBAdapter):

    DEFAULT_SERVER = 'caelus'
    SIMULATION_OUTPUTS = 'SIM_OUT'

    @staticmethod
    def acquire_client():
        mongo_uri = 'mongodb://mongo/' if 'IN_DOCKER' in environ else 'mongodb://localhost/'
        
        client = MongoClient(mongo_uri, 27017, connectTimeoutMS=5 * 1000)
        while True:
            print(f'Trying to acquire MongoDB connection at {mongo_uri}')
            try:
                client.admin.command('ping')
                return client
            except:
                pass
        return None        

    def __init__(self, client, operation_id, group_id, flush_every_seconds=1):
        super().__init__()
        self.name = 'MongoDB Writer'
        self.daemon = True
        self.__operation_id = operation_id
        self.__group_id = group_id
        self.__handle = client[MongoDBWriter.DEFAULT_SERVER][MongoDBWriter.SIMULATION_OUTPUTS]
        self.__data_buffer = {}
        self.__thread_queue = Queue()
        self.__flush_every_seconds = flush_every_seconds
        self.__should_stop = False
        self.__logger = logging.getLogger()
        self.__delete_old_data()

    def __delete_old_data(self):
        # Check if the database contains a document with the same operation id and group id
        # if so delete it
        self.__handle.delete_one({'operation_id':self.__operation_id, 'group_id': self.__group_id})
        
    def __dump_buffer(self):
        self.__store()
        self.__data_buffer = {}

    def __process_items(self, last):
        try:
            data, series = self.__thread_queue.get()
            for k,v in data.items():
                if k not in self.__data_buffer:
                    self.__data_buffer[k] = [] if series else 0
                if series:
                    self.__data_buffer[k].append(v)
                else:
                    self.__data_buffer[k] = v
        except Exception as e:
            self.__logger.warn('Failed in getting queue elements for DB write operation')
            self.__logger.warn(e)
        finally:
            now = time.time()
            if now - last >= self.__flush_every_seconds:
                last = now
                self.__dump_buffer()

    def run(self):
        last = time.time()
        while not self.__should_stop:
            self.__process_items(last)

    def update_query_for(self, data):
        
        PUSH = '$push'
        EACH = '$each'
        SET = '$set'

        query = { PUSH : {}, SET : {} }
        for k,v in data.items():
            if type(v) == list and len(v) > 0:
                query[PUSH][k] = {EACH:v}
            else:
                query[SET][k] = v

        return query

    def __store(self):
        try:
            query = self.update_query_for(self.__data_buffer)
            self.__handle.update_one({'operation_id':self.__operation_id, 'group_id': self.__group_id}, query, upsert=True)
        except Exception as e:
            print(e)

    def cleanup(self):
        self.__logger.info("Dumping database buffer...")
        self.__should_stop = True
        total_to_process = max(self.__thread_queue.qsize(), 1)
        logger_throttle = total_to_process
        while not self.__thread_queue.empty():
            left = self.__thread_queue.qsize()
            if left < logger_throttle:
                self.__logger.info(f'Processed {int((1 - self.__thread_queue.qsize() / total_to_process)*100)}%')
                logger_throttle = max(logger_throttle - (total_to_process / 10), 0)
            self.__process_items(time.time()+5+self.__flush_every_seconds) # always in the future
        
        self.__logger.info('Writing buffer...')
        self.__dump_buffer()
            

    def store(self, data, series=True):
        if not self.__should_stop:
            self.__thread_queue.put_nowait((data, series))
