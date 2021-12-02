from ..Logger import Logger
from .JSONDeserialiser import JSONDeserialiser
from ..Helpers.AttrDict import AttrDict

class FlightVolume(JSONDeserialiser):

    @staticmethod
    def get_centre_of_convex_hull(coordinates, max_alt, min_alt):
        xs = [latitude for latitude,_ in coordinates]
        ys = [longitude for _,longitude in coordinates]
        return [
            max(xs) - ((max(xs) - min(xs)) / 2),
            max(ys) - ((max(ys) - min(ys)) / 2),
            min_alt + (max_alt - min_alt) / 2
        ]    

    @staticmethod
    def feet_to_meters(feet):
        return feet / 3.281

    def __init__(self, json, logger=Logger()):
        super().__init__(json, logger=logger)
        self.__flatten()

    def get_object_properties(self):
        return [
            'volumes', 'time_start', 'time_end'
        ]

    def __flatten(self):
        volumes_dict = AttrDict.from_nested_dicts(self.volumes)
        self.altitude_agl = FlightVolume.feet_to_meters(volumes_dict.altitude_agl.value)
        self.altitude_lower_w84 = FlightVolume.feet_to_meters(volumes_dict.altitude_lower_w84.value)
        self.altitude_upper_w84 = FlightVolume.feet_to_meters(volumes_dict.altitude_upper_w84.value)
        # there seems to be an extra list wrapper around the coordinate array
        self.coordinates = volumes_dict.outline_polygon.coordinates[0]

    def get_centre(self):
        return FlightVolume.get_centre_of_convex_hull(self.coordinates, self.altitude_upper_w84, self.altitude_lower_w84)

    def __repr__(self):
        return f'<FlightVolume>'