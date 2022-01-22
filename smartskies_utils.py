from ast import arg
from dis import dis
import os
from pyclbr import Function
from dotenv import load_dotenv
from matplotlib.pyplot import close
from pyrsistent import m
load_dotenv()
from PySmartSkies.DIS_API import DIS_API
from PySmartSkies.CVMS_API import CVMS_API
from PySmartSkies.Credentials import DIS_Credentials, CVMS_Credentials
from PySmartSkies.Session import Session
from consolemenu import *
from consolemenu.items import *
from mission_generator import mission_generator

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
    return list(map(lambda xs: xs[0], dis_api.get_accepted_deliveries()))

def verb_for_operation_close(status):
    if status in ['Activated', "Non-Conforming", "Contingent"]:
        return 'End'
    else:
        return 'Cancel'

def abort_delivery_and_operation(dis_api, _id):
    res = dis_api.abort_delivery(_id)
    if res:
        print(f'\t> Delivery aborted')
    operation = dis_api.get_operation_details_with_delivery_id(_id)
    res = dis_api.end_or_close_delivery(_id, verb=verb_for_operation_close(operation.state))
    if res:
        print(f'\t> Operation closed')

def abort_deliveries_and_operations(dis_api: DIS_API):
    def considered_for_abort(status):
        return status not in ['DELIVERY_ABORTED', 'MISSION_COMPLETE']
    def considered_for_close(status):
        return status not in ['Ended', "Invalid"]
    aborted_deliveries, closed_operations = 0, 0
    print(f'Aborting all deliveries...')
    deliveries = [(delivery.id, delivery) for delivery in get_accepted_deliveries(dis_api)]
    for _id, delivery in deliveries:
        print(f'- {_id}')
        if considered_for_abort(delivery.delivery_status):
            res = dis_api.abort_delivery(_id)
            if res:
                print(f'\t> Delivery aborted')
                aborted_deliveries += 1
        operation = dis_api.get_operation_details_with_delivery_id(_id)
        if considered_for_close(operation.state):
            res = dis_api.end_or_close_delivery(_id, verb=verb_for_operation_close(operation.state))
        if res:
            print(f'\t> Operation closed')
            closed_operations += 1
    print(f'Aborted {aborted_deliveries} deliveries')
    print(f'Closed {closed_operations} operations')
    input('Press enter to continue...')

class DeliveryActions(FunctionItem):
    
    def __init__(self, dis_api, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dis_api: DIS_API = dis_api

    def action(self):
        r = super().action()
        return self.delivery_choice_submenu()

    def action_factory(self, action, name, *args):
        def action_and_pause():
            action(*args)
            input("Press enter to continue")
        return FunctionItem(name, action_and_pause)

    def abort_action(self, _id):
        return self.action_factory(abort_delivery_and_operation, "Abort Delivery and operation", self.__dis_api, _id)

    def actions_menu(self, delivery_id):
        menu = ConsoleMenu("Choose an action")
        abort = self.abort_action(delivery_id)
        menu.append_item(abort)
        return menu

    def delivery_choice_submenu(self):
        deliveries = self.get_return()
        if len(deliveries) == 0:
            print(f'No deliveries found with that filter.')
            input("Press enter to continue")
            return
        items = [(f'ID: {d.id} ({d.delivery_status})',d) for d in deliveries]
        menu = SelectionMenu(list(map(lambda a: a[0], items)), title="Select a delivery")
        menu.show()
        try:
            delivery_id = items[menu.selected_option][1].id
            self.actions_menu(delivery_id).show()
        except Exception as e:
            print(e)
            input()

def delivery_filters_menu(dis_api):
    def filter_by_status(deliveries, s):
        return [d for d in deliveries if d.delivery_status == s]

    f_all = DeliveryActions(dis_api, "All", lambda: get_accepted_deliveries(dis_api))
    other = [DeliveryActions(dis_api, filter_status, lambda f: filter_by_status(get_accepted_deliveries(dis_api), f), args=[filter_status]) for filter_status in ['DELIVERY_REQUEST_ACCEPTED', 'DELIVERY_INVALID', 'DELIVERY_ABORTED']]
    fs = [f_all] + other
    menu = ConsoleMenu('Filter by')
    for f in fs:
        menu.append_item(f)
    return menu

def build_menu(cvms_api, dis_api):
    menu = ConsoleMenu("Smartskies Utilities", "Manage smartskies deliveries and orders")
    delivery_filter = SubmenuItem("Find delivery", delivery_filters_menu(dis_api))
    abort_all = FunctionItem("Abort all deliveries and operations", abort_deliveries_and_operations, args=[dis_api])
    generate_mission = FunctionItem("New Mission", mission_generator, args=[cvms_api, dis_api])
    menu.append_item(delivery_filter)
    menu.append_item(abort_all)
    menu.append_item(generate_mission)
    return menu

build_menu(*authenticate()).show()