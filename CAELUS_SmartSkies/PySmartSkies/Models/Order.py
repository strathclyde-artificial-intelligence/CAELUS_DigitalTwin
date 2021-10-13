from ..Logger import Logger
from .JSONDeserialiser import JSONDeserialiser

class Order(JSONDeserialiser):

    def __init__(self, json, logger=Logger()):
        super().__init__(json, logger=logger)
    
    def get_object_properties(self):
        return [
            'id', 'ordered_by_user_id', 'store_id'
        ]

    def __repr__(self):
        return f'<Order|id={self.id}>'