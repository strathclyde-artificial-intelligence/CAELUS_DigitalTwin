from ast import arg
from dis import dis
import os
from dotenv import load_dotenv
load_dotenv()
from PySmartSkies.DIS_API import DIS_API
from PySmartSkies.CVMS_API import CVMS_API
from PySmartSkies.Credentials import DIS_Credentials, CVMS_Credentials
from PySmartSkies.Session import Session

from consolemenu import *
from consolemenu.items import *

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

def get_accepted_deliveries(dis_api: DIS_API):
    return dis_api.get_accepted_deliveries()

def abort_deliveries_and_operations(dis_api: DIS_API):
    def considered_for_abort(status):
        return status not in ['DELIVERY_ABORTED', 'MISSION_COMPLETE']
    def considered_for_close(status):
        return status not in ['Ended', "Invalid"]
    def verb_for_operation_close(status):
        if status in ['Activated', "Non-Conforming", "Contingent"]:
            return 'End'
        else:
            return 'Cancel'
    print(f'Aborting all deliveries...')
    deliveries = [(delivery.id, delivery) for delivery, _ in get_accepted_deliveries(dis_api)]
    for _id, delivery in deliveries:
        print(f'- {_id}')
        if considered_for_abort(delivery.delivery_status):
            res = dis_api.abort_delivery(_id)
            if res:
                print(f'\t> Delivery aborted')
        operation = dis_api.get_operation_details_with_delivery_id(_id)
        if considered_for_close(operation.state):
            res = dis_api.end_or_close_delivery(_id, verb=verb_for_operation_close(operation.state))
        if res:
            print(f'\t> Operation closed')

def build_menu(cvms_api, dis_api):
    menu = ConsoleMenu("Smartskies Utilities", "Manage smartskies deliveries and orders")
    delivery_states = SelectionMenu(["All", "Accepted", "Invalid", "Aborted", "By delivery ID"])
    get_acc_deliveries = SubmenuItem("Find Delivery", delivery_states, menu)
    abort_all = FunctionItem("Abort all deliveries and operations", abort_deliveries_and_operations, args=[dis_api])
    menu.append_item(get_acc_deliveries)
    menu.append_item(abort_all)
    return menu

build_menu(*authenticate()).show()