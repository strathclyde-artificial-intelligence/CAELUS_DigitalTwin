from ..Logger import Logger
from abc import ABC, abstractmethod

class JSONDeserialiser():
    def __init__(self, json, logger=Logger()):
        self._json = json
        self.__logger = logger
        self.__deserialise()
    
    def parse_key(self, key):
        if key not in self._json:
            self.__logger.warn(f'Key "{key}" not in the JSON object')
            return None
        return self._json[key]

    @abstractmethod
    def get_object_properties(self):
        pass

    def __deserialise(self):
        for key in self.get_object_properties():
            self.__dict__[key] = self.parse_key(key)