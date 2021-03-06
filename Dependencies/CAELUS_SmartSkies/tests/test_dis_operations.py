import pytest
from PySmartSkies.CVMS_API import CVMS_API
from PySmartSkies.DIS_API import DIS_API
from PySmartSkies.Session import Session
from PySmartSkies.Credentials import DIS_Credentials,CVMS_Credentials
from credentials import cvms_credentials, dis_credentials
from PySmartSkies.Models.Delivery import Delivery
from PySmartSkies.Models.Drone import Drone
from PySmartSkies.Models.Pilot import Pilot
from PySmartSkies.Models.ControlArea import ControlArea
from PySmartSkies.Models.Operation import Operation
from PySmartSkies.Models.FlightVolume import FlightVolume
from PySmartSkies.DeliveryStatus import STATUS_READY_FOR_DELIVERY

authenticated_api = None
viable_delivery = None
viable_drone = None
viable_control_area = None
viable_operation = None
operation_id = None

@pytest.fixture(autouse=True)
def authenticate_dis():
    global authenticated_api
    if authenticated_api is None:
        session = Session(dis_credentials, dis_credentials)
        api = DIS_API(session)
        api.authenticate()
        authenticated_api = api
    yield


def test_get_requested_deliveries():
    global viable_delivery
    global viable_drone
    global viable_control_area
    deliveries, pilots, drones, control_areas = authenticated_api.get_requested_deliveries()
    for delivery in deliveries:
            assert delivery is not None
            assert isinstance(delivery, Delivery)
            if viable_delivery is None:
                viable_delivery = delivery
    for pilot in pilots:
            assert pilot is not None
            assert isinstance(pilot, Pilot)
    for i,drone in enumerate(drones):
            assert drone is not None
            assert isinstance(drone, Drone)
            if viable_drone is None and i >= 2:
                viable_drone = drone
    for control_area in control_areas:
            assert control_area is not None
            assert isinstance(control_area, ControlArea)
            if viable_control_area is None:
                viable_control_area = control_area

def test_create_operation():
    global viable_operation
    response = authenticated_api.create_operation(viable_delivery, viable_drone, viable_control_area)
    for op in response:
        assert op is not None
        assert op.operation_volumes is not None
        assert isinstance(op, Operation)
        assert isinstance(op.operation_volumes, list)
        assert isinstance(op.operation_volumes[0], FlightVolume)
        assert isinstance(op.operation_volumes[0].coordinates, list)
        # assert each coordinate is a x,y point (lat, lon)
        assert len(op.operation_volumes[0].coordinates[0]) == 2
        if viable_operation is None:
            viable_operation = op
    
def test_generate_waypoints_from_operation():
    waypoints = viable_operation.get_waypoints()
    assert waypoints is not None
    for x,y,z in waypoints:
        assert isinstance(x, float)
        assert isinstance(y, float)
        assert isinstance(z, float)

def test_get_accepted_deliveries():
    deliveries = authenticated_api.get_accepted_deliveries()
    for delivery, flight_volumes in deliveries:
        assert delivery is not None
        assert flight_volumes is not None
        assert len(flight_volumes) > 0
        assert isinstance(delivery, Delivery)
        assert isinstance(flight_volumes[0], FlightVolume)

def test_get_operation_details():
    global operation_id
    operation = authenticated_api.get_operation_details_with_delivery_id(viable_delivery.id)
    operation_id = operation.operation_id
    assert operation is not None
    assert isinstance(operation, Operation)

def test_get_delivery_eta():
    eta = authenticated_api.get_delivery_eta(viable_delivery.id)
    assert isinstance(eta, float)
    assert eta >= 0

def test_delivery_status_update():
    assert authenticated_api.delivery_status_update(viable_delivery.id, STATUS_READY_FOR_DELIVERY)
    
def test_provide_clearance_update():
    assert authenticated_api.provide_clearance_update(viable_delivery.id)

def test_request_after_token_expiry():
    import time
    session = Session(dis_credentials, dis_credentials)
    api = DIS_API(session)
    api.authenticate()
    session.store_dis_bearer(session.get_dis_token(), session.get_dis_refresh_token(), time.time())
    test_get_requested_deliveries()

def test_get_delivery_status_id():
    status = authenticated_api.get_delivery_status_id(viable_delivery.id)
    assert status > 0

def test_get_weather_data():
    res = authenticated_api.get_weather_data(-4.296904760251587, 55.86692404205023)
    assert res is not None

def test_abort_delivery():
    response = authenticated_api.abort_delivery(viable_delivery.id)
    assert response is not None
    assert response['status_code'] == 200

def test_close_delivery_operation():
    response = authenticated_api.end_or_close_delivery(viable_delivery.id, 'Cancel')
    assert response is not None
