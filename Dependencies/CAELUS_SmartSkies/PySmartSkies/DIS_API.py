from typing import List, Tuple
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

class DIS_API():

    base_auth_endpoint = f'https://oauth.flyanra.net'
    base_endpoint = f'https://ss-anrademo-dis.flyanra.net'
    auth_endpoint = f'{base_auth_endpoint}/auth/realms/ANRA/protocol/openid-connect/token'
    requested_deliveries_endpoint = f'{base_endpoint}/selectbox_lists'
    create_operation_endpoint = f'{base_endpoint}/create_operation'
    get_accepted_deliveries_endpoint = f'{base_endpoint}/telemetry_list'
    get_operation_details_with_delivery_id_endpoint = f'{base_endpoint}/operations/'
    get_delivery_eta_endpoint = lambda delivery_id: f'{DIS_API.base_endpoint}/delivery/{delivery_id}/eta'
    provide_clearance_update_endpoint = f'https://dms-api-dev.flyanra.net/updatedronestatus' # why is this different than all others?
    delivery_status_update_endpoint = f'{base_endpoint}/delivery/status'
    end_or_close_delivery_endpoint = lambda delivery_id: f'{DIS_API.base_endpoint}/{delivery_id}/status'

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
    def __get_requested_deliveries(session):
        return GET_Request(DIS_API.requested_deliveries_endpoint, {}, bearer_token=session.get_dis_token())

    @staticmethod
    def __create_operation(session, delivery, drone, control_area, effective_time_begin=None):
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
            'flight_speed': 7,
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
            'status': 'CLEAR_FOR_TAKEOFF_CUSTOMER'
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

    def __init__(self, session, logger=Logger()):
        self._logger = logger
        if session is None:
            self._logger.fatal('Attempted to construct DIS_API with an empty Session.')
        self._session = session

    def authenticate(self):
        self._logger.info('Authenticating DIS user.')
        if self._session.get_dis_credentials() is None:
            self._logger.fatal('Trying to authenticate with the DIS service without having specified DIS credentials in the Session constructor.')
        auth_request = DIS_API.__auth_request(self._session)
        response = auth_request.send()
        if response is None or 'access_token' not in response:
            self._logger.fatal('Error while authenticating CVMS user.')
        bearer = response['access_token']
        self._session.store_dis_bearer(f'Bearer {bearer}')

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
        return operation

    def get_delivery_eta(self, delivery_id) -> float:
        response = self.__get_delivery_eta(self._session, delivery_id).send()
        eta = float(response['data']['eta'])
        return eta

    def provide_clearance_update(self, delivery_id) -> bool:
        response = self.__provide_clearance_update(self._session, delivery_id).send()
        return response['result'] or False

    # Status values can be found in DeliveryStatus.py
    def delivery_status_update(self, delivery_id, new_status) -> bool:
        response = self.__delivery_status_update(self._session, delivery_id, new_status).send()
        return response['status_code'] == 200

    def end_or_close_delivery(self, delivery_id):
        response = self.__end_or_close_delivery(self._session, delivery_id).send()
        if response is not None and 'status_code' in response and response['status_code'] == 200:
            return response