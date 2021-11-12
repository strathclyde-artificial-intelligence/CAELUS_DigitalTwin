import os
from PySmartSkies.Models.Operation import Operation
from dotenv import load_dotenv
from PySmartSkies.DIS_API import DIS_API
from PySmartSkies.CVMS_API import CVMS_API
from PySmartSkies.Credentials import DIS_Credentials, CVMS_Credentials
from PySmartSkies.Session import Session
import json

load_dotenv()

dis_credentials = DIS_Credentials(
    os.environ['DIS_GRANT_TYPE'],
    os.environ['DIS_CLIENT_ID'],
    os.environ['DIS_USERNAME'],
    os.environ['DIS_PASSWORD']
)

cvms_credentials = CVMS_Credentials(
    os.environ['CVMS_PHONE'],
    os.environ['CVMS_PASSWORD'],
    os.environ['CVMS_DEVICE_ID']
)

def authenticate():
    session = Session(cvms_credentials, dis_credentials)
    dis_api = DIS_API(session)
    dis_api.authenticate()
    cvms_api = CVMS_API(session)
    cvms_api.authenticate()
    return cvms_api, dis_api

def pp_vendors_and_products(vendors, products):
    vids = {str(v.id):v for v in vendors}

    for v_id, ps in products.items():
        if len(ps) == 0:
            continue
        print(f'Vendor: {vids[v_id].name} (id: {v_id})')
        for p in ps: 
            print(f"\t> {p}")

def get_possible_vendors_and_products(dis_api: DIS_API, cvms_api: CVMS_API):
    vendors = cvms_api.get_vendor_list()
    
    products = {
        str(v.id):cvms_api.get_product_list_from_vendor(v.id) for v in vendors
    }

    return vendors, products

def make_order(cvms_api: CVMS_API, product, vendor):
    res = cvms_api.place_order(vendor, [product])
    o = cvms_api.checkout_orders(res)

def make_operation(dis_api: DIS_API):
    deliveries, pilots, drones, control_areas = dis_api.get_requested_deliveries()
    ops = dis_api.create_operation(deliveries[-1], drones[-1], control_areas[-1])
    op: Operation = ops[0]
# {
#     "waypoints": [[-5.130347001, 55.573712, 30.478512648582747], [-5.126808347206886, 55.566402296603336, 30.478512648582747], [-5.1232696094686, 55.55909267367773, 30.478512648582747], [-5.119730787844276, 55.55178313116838, 30.478512648582747], [-5.11619188239305, 55.54447366902043, 30.478512648582747]],
#     "operation_id": "some_id",
#     "control_area_id": "some_control_area_id",
#     "operation_reference_number": "some_reference",
#     "drone_id": "some_id",
#     "drone_registration_number": "some_drone_registration_number",
#     "dis_auth_token": "some_auth_token",
#     "thermal_model_timestep": 1,
#     "aeroacoustic_model_timestep": 0.004,
#     "drone_config":{},
#     "g_acceleration": 9.81,
#     "initial_lon_lat_alt": [-5.1303470010000005, 55.573712, 2.6]
# }
    wps = op.get_waypoints()
    print(wps)
    payload = {
        'waypoints': wps,
        "operation_id": "some_id",
        "control_area_id": "some_control_area_id",
        "operation_reference_number": "some_reference",
        "drone_id": "some_id",
        "drone_registration_number": "some_drone_registration_number",
        "dis_auth_token": "some_auth_token",
        "thermal_model_timestep": 1,
        "aeroacoustic_model_timestep": 0.004,
        "drone_config":{},
        "g_acceleration": 9.81,
        "initial_lon_lat_alt": wps[0]
    }

    print(json.dumps(payload))

def parse_product_and_vendor(s, vendors, products):
    vendor_id, product_id = s.split('-')
    print(f'Chosen vendor: {vendor_id}, product: {product_id}')
    return list(filter(lambda v: str(v.id) == vendor_id, vendors))[0], list(filter(lambda p: str(p.id) == product_id, products[vendor_id]))[0]
        
cvms, dis = authenticate()
vs, ps = get_possible_vendors_and_products(dis, cvms)
pp_vendors_and_products(vs, ps)
s = input("Vendor number - Product number: ")
chosen_vendor, chosen_product = parse_product_and_vendor(s, vs, ps)
make_order(cvms,chosen_product, chosen_vendor)
make_operation(dis)