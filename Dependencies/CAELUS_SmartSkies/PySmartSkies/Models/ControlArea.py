from ..Logger import Logger
from .JSONDeserialiser import JSONDeserialiser

class ControlArea(JSONDeserialiser):

    def __init__(self, json, logger=Logger()):
        super().__init__(json, logger=logger)
    
    def get_object_properties(self):
        return [
            'control_area_id', 'ansp_id', 'user_id', 'control_area_name'
        ]

    def __repr__(self):
        return f'<ControlArea|id={self.control_area_id},name={self.control_area_name}>'