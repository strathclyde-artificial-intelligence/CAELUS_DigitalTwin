from PySmartSkies.Credentials import CVMS_Credentials, DIS_Credentials
from PySmartSkies.CVMS_API import CVMS_API
from PySmartSkies.DIS_API import DIS_API
from PySmartSkies.Session import Session
from random import choice, random

class MissionHelper():
    @staticmethod
    def __credentials(cred_dict):
        return {
            'cvms':CVMS_Credentials(
                cred_dict['CVMS_PHONE'],
                cred_dict['CVMS_PASSWORD'],
                cred_dict['CVMS_DEVICE_ID']
            ),
            'dis': DIS_Credentials(
                cred_dict['DIS_GRANT_TYPE'],
                cred_dict['DIS_CLIENT_ID'],
                cred_dict['DIS_USERNAME'],
                cred_dict['DIS_PASSWORD']
           )
        }

    def __init__(self, cred_dict):
        self.__credentials = MissionHelper.__credentials(cred_dict)
        self.__setup_api()

    def __setup_api(self):
        self.__session = Session(self.__credentials['cvms'], self.__credentials['dis'])
        self.dis_api = DIS_API(self.__session)
        self.cvms_api = CVMS_API(self.__session)
        self.__authenticate()

    def __authenticate(self):
        self.dis_api.authenticate()
        self.cvms_api.authenticate()

    def example_mission_waypoints(self):
        test_vendor = list(filter(lambda v: 'vendor' in v.name and v.address == 'Lady Margaret Hospital, vendor', self.cvms_api.get_vendor_list()))[0]
        random_product = choice(self.cvms_api.get_product_list_from_vendor(test_vendor.id))
        orders = self.cvms_api.place_order(test_vendor, [random_product])
        self.cvms_api.checkout_orders(orders)

        deliveries, pilots, drones, control_areas = self.dis_api.get_requested_deliveries()
        drone = drones[2]
        operations = self.dis_api.create_operation(deliveries[-1], drone, control_areas[0])
        delivery, _ = self.dis_api.get_accepted_deliveries()[0]
        
        return operations[0], delivery.operation_id, drone, self.dis_api._session.get_dis_token()