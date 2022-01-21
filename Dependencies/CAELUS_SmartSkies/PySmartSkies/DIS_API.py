from geojson import Point, LineString, loads
from json import dumps
from geomet import wkt
from typing import List, Tuple, Union
import datetime
from .Logger import Logger
from .Request import GET_Request, POST_Request, BodyType
from .Models.Delivery import Delivery
from .Models.Pilot import Pilot
from .Models.Drone import Drone
from .Models.ControlArea import ControlArea
from .Models.Operation import Operation
from .Models.FlightVolume import FlightVolume
from .DeliveryStatus import *
import time

class ParameterException(Exception):
    pass

class DIS_API():
    
    CONSTRAINT_TYPES = ['obstacle', 'population', 'terrain', 'danger', 'enroute', 'restricted', 'celltowers']

    base_auth_endpoint = f'https://oauth.flyanra.net'
    base_aware_endpoint = f'https://spatialdev.flyanra.net/aware/api'
    base_endpoint = f'https://ss-anrademo-dis.flyanra.net'
    auth_endpoint = f'{base_auth_endpoint}/auth/realms/ANRA/protocol/openid-connect/token'
    refresh_token_endpoint = f'{base_auth_endpoint}/auth/realms/ANRA/protocol/openid-connect/token'
    requested_deliveries_endpoint = f'{base_endpoint}/selectbox_lists'
    get_delivery_status_endpoint = f'https://dms-api-dev.flyanra.net/order/delivery_details'
    create_operation_endpoint = f'{base_endpoint}/create_operation'
    get_accepted_deliveries_endpoint = f'{base_endpoint}/telemetry_list'
    get_operation_details_with_delivery_id_endpoint = f'{base_endpoint}/operations/'
    get_delivery_eta_endpoint = lambda delivery_id: f'{DIS_API.base_endpoint}/delivery/{delivery_id}/eta'
    abort_delivery_endpoint = lambda delivery_id: f'{DIS_API.base_endpoint}/delivery/{delivery_id}/abort'
    provide_clearance_update_endpoint = f'https://dms-api-dev.flyanra.net/updatedronestatus' # why is this different than all others?
    delivery_status_update_endpoint = f'{base_endpoint}/delivery/status'
    end_or_close_delivery_endpoint = lambda delivery_id: f'{DIS_API.base_endpoint}/{delivery_id}/status'
    # AWARE
    get_constraints_endpoint = f'{base_aware_endpoint}/constraint'

    @staticmethod   
    def __auth_request(session):
        dis_credentials = session.get_dis_credentials()
        return POST_Request(DIS_API.auth_endpoint, {
            'grant_type':dis_credentials.grant_type,
            'client_id':dis_credentials.client_id,
            'username':dis_credentials.username,
            'password':dis_credentials.password
        }, body_type=BodyType.FORM_ENCODED)
    
    @staticmethod
    def __token_refresh_request(session):
        return POST_Request(DIS_API.refresh_token_endpoint, {
            'grant_type':'refresh_token',
            'client_id': 'DMS',
            'refresh_token': session.get_dis_refresh_token()
        }, body_type=BodyType.FORM_ENCODED)

    @staticmethod
    def __get_requested_deliveries(session):
        return GET_Request(DIS_API.requested_deliveries_endpoint, {}, bearer_token=session.get_dis_token())

    @staticmethod
    def __create_operation(session, delivery, drone, control_area, effective_time_begin=None, expected_cruise_speed=7):
        if effective_time_begin is None:
            effective_time_begin = datetime.datetime.utcnow()
            effective_time_begin += datetime.timedelta(minutes=30)
            effective_time_begin = effective_time_begin.isoformat()

        return POST_Request(DIS_API.create_operation_endpoint, {
            'delivery_id': delivery.id,
            'control_area_id': control_area.control_area_id,
            'organization_id': drone.organization_id,
            'ansp_id': drone.ansp_id,
            'user_id': control_area.user_id,
            'drone_id': drone.drone_id,
            'vender_coordinate': delivery.pickup_coordinate,
            'customer_coordinate': delivery.dropoff_coordinate,
            'altitude': 200,
            'takeoff_landing_radius': 100,
            'flight_speed': expected_cruise_speed, # miles/h
            'altitude_buffer': 100,
            'expand_factor': "LOW",
            'effective_time_begin': effective_time_begin,
            'facility': "DIS"
        }, bearer_token=session.get_dis_token())
    
    @staticmethod
    def __end_or_close_delivery(session, delivery_id):
        return POST_Request(DIS_API.end_or_close_delivery_endpoint(delivery_id), { "status_type":"End" }, bearer_token=session.get_dis_token())

    @staticmethod
    def __get_accepted_deliveries(session):
        return GET_Request(DIS_API.get_accepted_deliveries_endpoint, {}, bearer_token=session.get_dis_token())

    @staticmethod
    def __provide_clearance_update(session, delivery_id):
        return POST_Request(DIS_API.provide_clearance_update_endpoint, {
            'delivery_id': delivery_id,
            'status': 'CLEAR_TO_LAND_CUSTOMER'
            }, bearer_token=session.get_dis_token())

    @staticmethod
    def __delivery_status_update(session, delivery_id, new_status):
        return POST_Request(DIS_API.delivery_status_update_endpoint, {
            "delivery_id": delivery_id,
            "delivery_status": new_status,
            "notes": "delivery status update"
        }, bearer_token=session.get_dis_token())

    @staticmethod
    def __get_operation_details_with_delivery_id(session, delivery_id):
        return GET_Request(f'{DIS_API.get_operation_details_with_delivery_id_endpoint}{delivery_id}', {}, bearer_token=session.get_dis_token())

    @staticmethod
    def __get_delivery_eta(session, delivery_id):
        return GET_Request(DIS_API.get_delivery_eta_endpoint(delivery_id), {}, bearer_token=session.get_dis_token())

    @staticmethod
    def __abort_delivery(session, delivery_id):
        return POST_Request(DIS_API.abort_delivery_endpoint(delivery_id), {}, bearer_token=session.get_dis_token())

    @staticmethod
    def __get_delivery_status(session, delivery_id):
        return GET_Request(DIS_API.get_delivery_status_endpoint, {'drone_delivery_id':delivery_id}, bearer_token=session.get_dis_token())

    @staticmethod
    def __get_constraint(session, type: str, location: Union[Point, LineString], range: int):
        """
        param type: one of CONSTRAINT_TYPES
        param location: (WKT) https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry
        param range: radius from location in meters
        """
        if type not in DIS_API.CONSTRAINT_TYPES:
            raise ParameterException(f'Constraint type not valid ({type} not in {DIS_API.CONSTRAINT_TYPES})')
        if not (isinstance(location, Point) or isinstance(location, LineString)):
            raise ParameterException(f'Location must be either a geojson Point or LineString')
        if range <= 0:
            raise ParameterException(f'Radius must be greater than zero if specified.')
        wkt_location = wkt.dumps(location, decimals=8)
        return GET_Request(DIS_API.get_constraints_endpoint, {
            'type': type,
            'location':wkt_location,
            'range': range
        }, bearer_token=session.get_dis_token())

    def __init__(self, session, logger=Logger()):
        self._logger = logger
        if session is None:
            self._logger.fatal('Attempted to construct DIS_API with an empty Session.')
        self._session = session
        self._session.set_refresh_closure(lambda: self.refresh_token())

    def __process_auth_payload(self, payload):
        try:
            if payload is None or 'access_token' not in payload:
                raise Exception('Error while refreshing token for DIS user.')
            bearer = payload['access_token']
            refresh = payload['refresh_token']
            expiry = time.time() + payload['expires_in']
            self._session.store_dis_bearer(f'Bearer {bearer}', refresh, expiry)
        except Exception as e:
            self._logger.fatal(f'Malformed authentication payload.')
            self._logger.fatal(e)

    def refresh_token(self):
        self._logger.info('Refreshing DIS user token.')
        refresh_request = DIS_API.__token_refresh_request(self._session)
        response = refresh_request.send()
        self.__process_auth_payload(response)

    def authenticate(self):
        self._logger.info('Authenticating DIS user.')
        if self._session.get_dis_credentials() is None:
            self._logger.fatal('Trying to authenticate with the DIS service without having specified DIS credentials in the Session constructor.')
        auth_request = DIS_API.__auth_request(self._session)
        response = auth_request.send()
        self.__process_auth_payload(response)

    def get_requested_deliveries(self) -> Tuple[List[Delivery], List[Pilot], List[Drone], List[ControlArea]]:
        response = self.__get_requested_deliveries(self._session).send()['data']
        if response is None:
            self._logger.fatal('Error while getting requested deliveries for authenticated DIS user.')
        
        requested_deliveries_json = response['requested_deliveries']
        pilot_list_json = response['pilot_list']
        drone_list_json = response['drone_list']
        control_area_list_json = response['control_area_list']

        deliveries = map(lambda json: Delivery({**json, 'operation_id': None}), requested_deliveries_json)
        pilots = map(lambda json: Pilot(json), pilot_list_json)
        drones = map(lambda json: Drone(json), drone_list_json)
        control_areas = map(lambda json: ControlArea(json), control_area_list_json)
        
        return list(deliveries), list(pilots), list(drones), list(control_areas)

    def create_operation(self, delivery, drone, control_area, effective_time_begin=None) -> List[Operation]:
        if delivery is None or drone is None or control_area is None:
            self._logger.fatal(f'Tried to create an operation with invalid parameters.')
        request = self.__create_operation(self._session, delivery, drone, control_area, effective_time_begin)
        response = request.send()['data']
        if response is None:
            self._logger.fatal(f'Error while creating an operation for delivery {delivery.id}')
        operations = map(lambda json: Operation(json), response)
        return list(operations)

    def get_accepted_deliveries(self) -> List[Tuple[Delivery, List[FlightVolume]]]:
        response = self.__get_accepted_deliveries(self._session).send()
        deliveries = map(lambda json: Delivery({**json['delivery'], 'operation_id': json['operation_id']}), response['data'])
        flight_volumes = map(lambda json: [FlightVolume(volume) for volume in json['operation_volumes']], response['data'])
        return list(zip(deliveries, flight_volumes))

    def get_operation_details_with_delivery_id(self, delivery_id) -> Operation:
        response = self.__get_operation_details_with_delivery_id(self._session, delivery_id).send()
        operation = None
        if response is not None and 'data' in response:
            operation = Operation(response['data'])
            # Needs to be specific to this response because of https://github.com/H3xept/CAELUS_SmartSkies/issues/5
            operation.operation_id = response['data']['operation_id']
        return operation

    def get_delivery_eta(self, delivery_id) -> float:
        response = self.__get_delivery_eta(self._session, delivery_id).send()
        eta = float(response['data']['eta'])
        return eta

    def get_delivery_status_id(self, delivery_id) -> int:
        response = self.__get_delivery_status(self._session, delivery_id).send()
        if response is not None and 'data' in response and 'drone_status_id' in response['data']:
            return response['data']['drone_status_id']
        else:
            self._logger.warn(f'Failed in requesting status for delivery {delivery_id}')
            return -1

    def abort_delivery(self, delivery_id):
        response = self.__abort_delivery(self._session, delivery_id).send()
        if response is None or response['status_code'] != 200:
            self._logger.warn(f'Delivery {delivery_id} not aborted.')
        return response
    def provide_clearance_update(self, delivery_id) -> bool:
        response = self.__provide_clearance_update(self._session, delivery_id).send()
        return response['result'] or False

    # Status values can be found in DeliveryStatus.py
    def delivery_status_update(self, delivery_id, new_status) -> bool:
        response = self.__delivery_status_update(self._session, delivery_id, new_status).send()
        if response is not None and 'status_code' in response:
            ret = response['status_code']
            if ret != 200:
                self._logger.warn('Status update failed with response: ')
                self._logger.warn(response)
            return ret
        return False

    def end_or_close_delivery(self, delivery_id):
        response = self.__end_or_close_delivery(self._session, delivery_id).send()
        if response is not None and 'status_code' in response and response['status_code'] == 200:
            return response

    # INFO: All AWARE endpoints return a FeatureCollection object from the GeoJSON library
    # Documentation here (https://pypi.org/project/geojson/#featurecollection)

    def get_aware_obstacle(self, location: Union[Point, LineString], range: int):
        response = self.__get_constraint(self._session, 'obstacle', location, range).send()
        if response is not None:
            return loads(dumps(response))
        self._logger.error(f'Endpoint "get_aware_obstacle" failed to respond.')

    def get_aware_population(self, location: Union[Point, LineString], range: int):
        response = self.__get_constraint(self._session, 'population', location, range).send()
        if response is not None:
            return loads(dumps(response))
        self._logger.error(f'Endpoint "get_aware_population" failed to respond.')

    def get_aware_terrain(self, location: Union[Point, LineString], range: int):
        response = self.__get_constraint(self._session, 'terrain', location, range).send()
        if response is not None:
            return loads(dumps(response))
        self._logger.error(f'Endpoint "get_aware_terrain" failed to respond.')

    def get_aware_danger(self, location: Union[Point, LineString], range: int):
        response = self.__get_constraint(self._session, 'danger', location, range).send()
        if response is not None:
            return loads(dumps(response))
        self._logger.error(f'Endpoint "get_aware_danger" failed to respond.')

    def get_aware_enroute(self, location: Union[Point, LineString], range: int):
        response = self.__get_constraint(self._session, 'enroute', location, range).send()
        if response is not None:
            return loads(dumps(response))
        self._logger.error(f'Endpoint "get_aware_enroute" failed to respond.')

    def get_aware_restricted(self, location: Union[Point, LineString], range: int):
        response = self.__get_constraint(self._session, 'restricted', location, range).send()
        if response is not None:
            return loads(dumps(response))
        self._logger.error(f'Endpoint "get_aware_restricted" failed to respond.')

    def get_aware_celltowers(self, location: Union[Point, LineString], range: int):
        response = self.__get_constraint(self._session, 'celltowers', location, range).send()
        if response is not None:
            return loads(dumps(response))
        self._logger.error(f'Endpoint "get_aware_celltowers" failed to respond.')