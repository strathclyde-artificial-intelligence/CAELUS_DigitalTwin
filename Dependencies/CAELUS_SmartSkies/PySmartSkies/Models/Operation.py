from math import ceil
from ..Logger import Logger
from .JSONDeserialiser import JSONDeserialiser
from .FlightVolume import FlightVolume
from pyproj import Geod
from ..Helpers.Sutherland_Hodgman import PolygonClipper
from itertools import chain, zip_longest

clipper = PolygonClipper()

def interleave(l1, l2):
    return [x for x in chain.from_iterable(zip_longest(l1, l2)) if x is not None]

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

    def __interpolate_with_max_distance(self, start, end, max_dist):
        def lerp(i_percentage, start_alt, end_alt):
            return (1 - i_percentage) * start_alt + i_percentage * end_alt
        geod = Geod(ellps='WGS84')
        az12,az21,dist = geod.inv(start[1], start[0], end[1], end[0])
        result = geod.fwd_intermediate(start[1],start[0],az12,npts=ceil(dist / max_dist),del_s=max_dist, initial_idx=0, terminus_idx=0)
        return [(lat_lon[0], lat_lon[1], lerp(i / len(result.lats), start[-1], end[-1])) for i, lat_lon in enumerate(zip(result.lats, result.lons))]

    def get_waypoints(self, max_distance=850):
        intersection_hulls = [
            clipper(self.operation_volumes[i].coordinates, self.operation_volumes[i+1].coordinates) for i in range(len(self.operation_volumes) - 1)
        ]
        intersection_centres = [
            FlightVolume.get_centre_of_convex_hull(intersection_hulls[i], self.operation_volumes[i].altitude_upper_w84, self.operation_volumes[i].altitude_lower_w84) for i in range(len(intersection_hulls))
        ]
        waypoints = [volume.get_centre() for volume in self.operation_volumes]
        waypoints = [waypoints[0]] + interleave(intersection_centres, waypoints[1:-1]) + [waypoints[-1]]
        latlons = []
        for i in range(len(waypoints) - 1):
            start = waypoints[i]
            end = waypoints[i+1]
            new_lats_lons = self.__interpolate_with_max_distance(start, end, max_distance)
            latlons.extend(new_lats_lons)
        return [(lat_lon_alt[0], lat_lon_alt[1], lat_lon_alt[2]) for lat_lon_alt in latlons] + [self.get_landing_location()]

    def get_takeoff_location(self):
        start_v = self.operation_volumes[0]
        lat, lon, _ = start_v.get_centre()
        alt = start_v.altitude_lower_w84
        return (lat, lon, alt)

    def get_landing_location(self):
        end_v = self.operation_volumes[-1]
        lat, lon, _ = end_v.get_centre()
        alt = end_v.altitude_lower_w84
        return (lat, lon, alt)

    def __repr__(self):
        return f'<Operation|reference={self.reference_number}>'