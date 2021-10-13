from ..Logger import Logger
from .JSONDeserialiser import JSONDeserialiser

class Customer(JSONDeserialiser):

    def __init__(self, json, logger=Logger()):
        super().__init__(json, logger=logger)
    
    def get_object_properties(self):
        return [
            'uid', 'uuid', 'name', 'address', 'phone', 'email'
        ]

    def __repr__(self):
        return f'<Customer|id={self.uid},name={self.name}>'