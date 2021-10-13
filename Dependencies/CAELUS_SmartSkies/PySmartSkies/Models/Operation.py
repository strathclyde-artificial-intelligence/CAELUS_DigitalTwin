from ..Logger import Logger
from .JSONDeserialiser import JSONDeserialiser
from .FlightVolume import FlightVolume

class Operation(JSONDeserialiser):

    def __init__(self, json, logger=Logger()):
        super().__init__(json, logger=logger)
        self.__process_volumes()

    def get_object_properties(self):
        return [
            # Operation ID missing as there seems to be an inconsistency between two endpoints that *should* return
            # operation objects
            # issue: https://github.com/H3xept/CAELUS_SmartSkies/issues/5
            'control_area_id', 'ansp_id', 'user_id', 'organization_id', 'operation_volumes', 'reference_number', 'proposed_flight_speed'
        ]

    def __process_volumes(self):
        self.operation_volumes = [FlightVolume(json) for json in self.operation_volumes]

    def get_waypoints(self):
        return [volume.get_centre() for volume in self.operation_volumes]
        
    def __repr__(self):
        return f'<Operation|reference={self.reference_number}>'