from ..Logger import Logger
from .JSONDeserialiser import JSONDeserialiser

class Product(JSONDeserialiser):

    def __init__(self, json, logger=Logger()):
        super().__init__(json, logger=logger)
    
    def get_object_properties(self):
        return [
            'id', 'name', 'store_id', 'state', 'per_item_weight'
        ]

    def __repr__(self):
        return f'<Product|id={self.id},name={self.name}>'