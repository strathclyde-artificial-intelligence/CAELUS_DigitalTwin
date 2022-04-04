from ..Logger import Logger
from .JSONDeserialiser import JSONDeserialiser

class Vendor(JSONDeserialiser):

    def __init__(self, json, logger=Logger()):
        super().__init__(json, logger=logger)
    
    def get_object_properties(self):
        return [
            'id', 'vendor_id', 'name', 'uuid', 'locationList', 'location_lat', 'location_long', 'address', 'location_text', 'maxChargingCapacity', 'maxStorageCapacity', 'isChargingStation'
        ]

    def __repr__(self):
        return f'<Vendor|id={self.id},name={self.name}>'