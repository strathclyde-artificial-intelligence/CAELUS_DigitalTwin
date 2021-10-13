from ..Logger import Logger
from .JSONDeserialiser import JSONDeserialiser

class Pilot(JSONDeserialiser):

    def __init__(self, json, logger=Logger()):
        super().__init__(json, logger=logger)
    
    def get_object_properties(self):
        return [
            'user_id', 'user_name', 'email', 'organization_id', 'ansp_id'
        ]

    def __repr__(self):
        return f'<Pilot|id={self.user_id},name={self.user_name}>'