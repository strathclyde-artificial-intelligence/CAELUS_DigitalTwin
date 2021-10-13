from ..Logger import Logger
from .JSONDeserialiser import JSONDeserialiser

class Drone(JSONDeserialiser):

    def __init__(self, json, logger=Logger()):
        super().__init__(json, logger=logger)
    
    def get_object_properties(self):
        return [
            'drone_id', 'drone_name', 'ansp_id', 'organization_id', 'registration_number'
        ]

    def __repr__(self):
        return f'<Drone|id={self.drone_id},name={self.drone_name}>'