import enum
import os
from uuid import uuid4
from PySmartSkies.Models.Operation import Operation
from dotenv import load_dotenv
from PySmartSkies.DIS_API import DIS_API
from PySmartSkies.CVMS_API import CVMS_API
from PySmartSkies.Credentials import DIS_Credentials, CVMS_Credentials
from PySmartSkies.Session import Session
import json
from Dependencies.CAELUS_SmartSkies.PySmartSkies.Models.Product import Product
from start import start_with_payload
import time
import pickle

def authenticate(cvms_credentials, dis_credentials):
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
            print(f'No products for vendor {v_id}')
        print(f'Vendor: {vids[v_id].name} (id: {v_id})')
        for p in ps: 
            print(f"\t> {p}")

def get_possible_vendors_and_products(dis_api: DIS_API, cvms_api: CVMS_API):
    VENDORS_PICKLE_F = 'vendors.pickle'
    try:
        with open(VENDORS_PICKLE_F, 'rb') as f:
            vs_ps = pickle.loads(f.read())
            return vs_ps['vendors'], vs_ps['products']
    except Exception as e:
        print(e)
        vendors = cvms_api.get_vendor_list(items_per_page=400)
        products = {
            str(v.id):cvms_api.get_product_list_from_vendor(v.id) for v in vendors
        }
        with open(VENDORS_PICKLE_F, 'wb') as f:
            s = pickle.dumps({'vendors':vendors, 'products':products})
            f.write(s)
        return vendors, products

def make_order(cvms_api: CVMS_API, product, vendor):
    res = cvms_api.place_order(vendor, [product])
    o = cvms_api.checkout_orders(res)
    return o, product

def drone_params_from_weight(base_w):
    # Should be able to lift 3 times its weight
    max_thrust = ((base_w * 3) * 9.81) / 4
    max_torque = (0.05 * base_w) / 0.8 # proportional to default torque
    return {'max_thrust': max_thrust, 'max_torque':max_torque, 'max_back_propeller_thrust':max_thrust * 2}
    

def get_drone_base_weight():
    while True:
        try:
            kg = float(input("Drone base weight (kg): "))
            if kg <= 0:
                raise Exception("Can't be lower or equal to zero")
            return kg
        except:
            pass

def prompt_selection(options: dict):
    keys = list(options.keys())
    while True:
        try:
            for i,k in enumerate(keys):
                print(f'{i}) {k}')
            selection = int(input(f'(0-{len(keys)-1}): '))
            if selection >= len(keys):
                raise Exception()
            return options[keys[selection]]
        except Exception as e:
            print(e)

def drone_selection():
    drone_conf = {}
    _type = prompt_selection({'quadrotor':0, 'fixed-wing':1})
    drone_conf.update({'type':_type})
    if _type == 1:
        drone_conf.update({'tail_length':0.30})
    return drone_conf

import datetime
def make_operation(dis_api: DIS_API, product: Product):
    deliveries, pilots, drones, control_areas = dis_api.get_requested_deliveries()
    if len(deliveries) == 0:
        print('Smartskies failed in creating delivery. Hospitals may be too far apart!')
        exit(-1)
    drone = drones[-1]
    # Operation begin in smartskies request
    effective_time_begin = datetime.datetime.utcnow()
    effective_time_begin += datetime.timedelta(minutes=1)
    # Orchestrator effective time start
    time_begin_unix = time.time() + 2 * 60 + 60
    ops = dis_api.create_operation(deliveries[-1], drone, control_areas[-1], effective_time_begin.isoformat())
    op_details = dis_api.get_operation_details_with_delivery_id(deliveries[-1].id)
    base_mass = get_drone_base_weight()
    op: Operation = ops[0]
    wps = op.get_waypoints()

    total_mass = base_mass + product.per_item_weight
    drone_config = drone_selection()
    drone_config.update({'mass':total_mass})
    drone_config.update(drone_params_from_weight(base_mass))

    if total_mass * 9.81 > 0.7 * drone_config['max_thrust']:
        print(f'[WARNING] Drone is too heavy -- there will be stabilty problems.')

    # Takeoff location must be rounded up / increased slightly
    # To prevent collision of the drone with the bottom of the
    # takeoff volume
    initial_lon_lat_alt_corrected = list(op.get_takeoff_location())
    initial_lon_lat_alt_corrected[-1] += 0.5
    # --------

    group_id = input("Group id (blank for auto generated ID): ")
    group_id = group_id if group_id != "" else str(uuid4())

    payload = {
        'waypoints': wps,
        "operation_id": op_details.operation_id,
        "control_area_id": control_areas[-1].control_area_id,
        "operation_reference_number": ops[-1].reference_number,
        "drone_id": drone.drone_id,
        "drone_registration_number": drone.registration_number,
        "dis_auth_token": dis_api._session.get_dis_token(),
        "dis_refresh_token": dis_api._session.get_dis_refresh_token(),
        "cvms_auth_token": dis_api._session.get_cvms_token(),
        "delivery_id": deliveries[-1].id,
        "thermal_model_timestep": 1,
        "aeroacoustic_model_timestep": 0.004,
        "drone_config":drone_config,
        "g_acceleration": 9.81,
        "group_id":group_id,
        "effective_start_time": time_begin_unix,
        "initial_lon_lat_alt": initial_lon_lat_alt_corrected,
        "final_lon_lat_alt":op.get_landing_location()
    }

    return json.dumps(payload)

def parse_product_and_vendor(s, vendors, products):
    vendor_id, product_id = s.split('-')
    print(f'Chosen vendor: {vendor_id}, product: {product_id}')
    return list(filter(lambda v: str(v.id) == vendor_id, vendors))[0], list(filter(lambda p: str(p.id) == product_id, products[vendor_id]))[0]

def mission_generator(cvms, dis):
    try:
        vs, ps = get_possible_vendors_and_products(dis, cvms)
        pp_vendors_and_products(vs, ps)
        s = input("Vendor number - Product number: ")
        chosen_vendor, chosen_product = parse_product_and_vendor(s, vs, ps)
        order, product = make_order(cvms,chosen_product, chosen_vendor)
        if order is not None and order['result']:
            print(f"Order successful ({order})")
            payload = make_operation(dis, product)
            print(payload)
    except Exception as e:
        print(e)
        input("Press enter to continue")

if __name__ == '__main__':
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
    cvms, dis = authenticate(cvms_credentials, dis_credentials)
    mission_generator(cvms, dis)