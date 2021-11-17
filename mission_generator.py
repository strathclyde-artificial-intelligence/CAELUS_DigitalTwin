import os
from PySmartSkies.Models.Operation import Operation
from dotenv import load_dotenv
from PySmartSkies.DIS_API import DIS_API
from PySmartSkies.CVMS_API import CVMS_API
from PySmartSkies.Credentials import DIS_Credentials, CVMS_Credentials
from PySmartSkies.Session import Session
import json
from start import start_with_payload

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
    return o

import datetime
def make_operation(dis_api: DIS_API):
    deliveries, pilots, drones, control_areas = dis_api.get_requested_deliveries()
    drone = drones[-2]
    print(deliveries)
    effective_time_begin = datetime.datetime.utcnow()
    effective_time_begin += datetime.timedelta(minutes=60)
    ops = dis_api.create_operation(deliveries[-1], drone, control_areas[-1], effective_time_begin.isoformat())
    op_details = dis_api.get_operation_details_with_delivery_id(deliveries[-1].id)
    
    op: Operation = ops[0]
    wps = op.get_waypoints()
    payload = {
        'waypoints': wps,
        "operation_id": op_details.operation_id,
        "control_area_id": control_areas[-1].control_area_id,
        "operation_reference_number": ops[-1].reference_number,
        "drone_id": drone.drone_id,
        "drone_registration_number": drone.registration_number,
        "dis_auth_token": dis_api._session.get_dis_token(),
        "thermal_model_timestep": 1,
        "aeroacoustic_model_timestep": 0.004,
        "drone_config":{},
        "g_acceleration": 9.81,
        "initial_lon_lat_alt": wps[0]
    }

    return json.dumps(payload)

def parse_product_and_vendor(s, vendors, products):
    vendor_id, product_id = s.split('-')
    print(f'Chosen vendor: {vendor_id}, product: {product_id}')
    return list(filter(lambda v: str(v.id) == vendor_id, vendors))[0], list(filter(lambda p: str(p.id) == product_id, products[vendor_id]))[0]

cvms, dis = authenticate()
vs, ps = get_possible_vendors_and_products(dis, cvms)
pp_vendors_and_products(vs, ps)
s = input("Vendor number - Product number: ")
chosen_vendor, chosen_product = parse_product_and_vendor(s, vs, ps)
order = make_order(cvms,chosen_product, chosen_vendor)
if order is not None and order['result']:
    print(f"Order successful ({order})")
    payload = make_operation(dis)
    print(payload)
#     start_with_payload(payload)