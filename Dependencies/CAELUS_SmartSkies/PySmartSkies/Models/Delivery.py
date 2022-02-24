from ..Logger import Logger
from .JSONDeserialiser import JSONDeserialiser

class Delivery(JSONDeserialiser):

    def __init__(self, json, logger=Logger()):
        super().__init__(json, logger=logger)
    
    def get_object_properties(self):
        return [
            'id', 'delivery_status', 'vendor_id', 'operator_id', 'customer_id', 'pickup_coordinate', 'dropoff_coordinate', 'pickup_time', 'dropoff_time', 'operation_id', 'submit_time'
        ]

    def __repr__(self):
        return f'<Delivery|id={self.id},status={self.delivery_status}>'