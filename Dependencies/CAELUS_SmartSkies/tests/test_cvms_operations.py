import pytest
from PySmartSkies.CVMS_API import CVMS_API
from PySmartSkies.DIS_API import DIS_API
from PySmartSkies.Session import Session
from PySmartSkies.Credentials import DIS_Credentials,CVMS_Credentials
from credentials import cvms_credentials, dis_credentials
from PySmartSkies.Models.Vendor import Vendor
from PySmartSkies.Models.Product import Product
from PySmartSkies.Models.Order import Order

authenticated_api = None
viable_vendor_id = None
viable_vendor = None
viable_buyer_id = None
viable_buyer = None
viable_product_id = None
viable_product = None
viable_order = None

@pytest.fixture(autouse=True)
def authenticate_cvms():
    global authenticated_api
    if authenticated_api is None:
        session = Session(cvms_credentials, dis_credentials)
        api = CVMS_API(session)
        api.authenticate()
        authenticated_api = api
    yield

def test_get_vendor_list():
    global viable_vendor_id
    global viable_vendor
    global viable_buyer_id
    global viable_buyer
    preferred_vendor_id = 66
    vendors = authenticated_api.get_vendor_list()
    for vendor in vendors:
        if viable_vendor_id is None and 'vendor' in vendor.name and vendor.id == preferred_vendor_id:
            viable_vendor_id = vendor.id
            viable_vendor = vendor
        if viable_buyer_id is None and 'vendor' not in vendor.name:
            viable_buyer_id = vendor.id
            viable_buyer = vendor
        assert vendor is not None and isinstance(vendor, Vendor)
    assert any([v.vendor_id == 180 for v in vendors])

def test_get_product_list_from_vendor():
    global viable_product_id
    global viable_product
    preferred_product_id = 103
    for product in authenticated_api.get_product_list_from_vendor(viable_vendor_id):
        if viable_product_id is None and product.id == preferred_product_id:
            viable_product_id = product.id
            viable_product = product
        assert product is not None and isinstance(product, Product)

def test_place_order():
    global viable_order
    response = authenticated_api.place_order(viable_vendor, [viable_product]*5)
    for o in response:
        assert isinstance(o, Order)
        if viable_order is None:
            viable_order = o
    

def test_checkout_order():
    response = authenticated_api.checkout_orders([viable_order])
    assert response is not None
    assert 'result' in response
    assert response['result']