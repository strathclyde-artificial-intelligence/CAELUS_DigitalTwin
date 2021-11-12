from functools import reduce

from .Logger import Logger
from .Request import GET_Request, POST_Request
from .Models.Vendor import Vendor
from .Models.Product import Product
from .Models.Customer import Customer
from .Models.Order import Order

class CVMS_API():

    base_endpoint = f'https://dms-api-dev.flyanra.net'
    auth_endpoint = f'{base_endpoint}/auth/loginByPhone'
    get_vendor_list_endpoint = f'{base_endpoint}/shop/store_list'
    get_product_list_endpoint = f'{base_endpoint}/shop/item_list'
    place_order_endpoint = f'{base_endpoint}/shop/place_order_add'
    checkout_order_endpoint = f'{base_endpoint}/order/split/checkout'
    
    @staticmethod
    def __auth_request(session):
        cvms_credentials = session.get_cvms_credentials()
        return POST_Request(CVMS_API.auth_endpoint, {
            'phone':cvms_credentials.phone,
            'password':cvms_credentials.password,
            'device_id':cvms_credentials.device_id
        })
    
    @staticmethod
    def __get_vendor_list(session, page_number=1, items_per_page=100):
        return GET_Request(CVMS_API.get_vendor_list_endpoint, {
            'pageNo':page_number,
            'itemPerPage':items_per_page
        }, bearer_token=session.get_cvms_token())
    
    @staticmethod
    def __get_product_list_from_vendor(session, shop_id, page_number=1, items_per_page=100):
        return GET_Request(CVMS_API.get_product_list_endpoint, {
            'shop_id':shop_id,
            'pageNo':page_number,
            'itemPerPage':items_per_page
        }, bearer_token=session.get_cvms_token())

    @staticmethod
    def __place_order(session, buyer: Vendor, seller: Vendor, products: [Product]):

        def process_products(products):
            prods = {}
            for product in products:
                if product.id not in prods:
                    prods[product.id] = {'item_id': product.id, 'quantity':1, 'per_item_weight':product.per_item_weight}
                else:
                    prods[product.id]['quantity'] += 1
            return list(prods.values())

        return POST_Request(CVMS_API.place_order_endpoint, {
            'address':buyer.address,
            'contact':buyer.phone, # is this the seller or buyer phone
            'delivery_charge': 0, # TODO: include
            'id': 0, # ??
            'orderQuantity': process_products(products),
            'order_status_id':0, # ??
            'order_total': len(products),
            'ordered_by_user_id': buyer.uid,
            'ordered_by_user_name': buyer.name,
            'store_id':seller.id,
            'store_name':seller.name,
            'updated_by': 0, # ??
            'updated_on': 0 # ??
        }, bearer_token=session.get_cvms_token())
    
    @staticmethod
    def __checkout_order(session, order_ids):
        return POST_Request(CVMS_API.checkout_order_endpoint, {
            'order_id_list':order_ids
        }, bearer_token=session.get_cvms_token())


    def __init__(self, session, logger=Logger()):
        self._logger = logger
        if session is None:
            self._logger.fatal('Attempted to construct CVMS_API with an empty Session.')
        self._session = session
        self._logged_customer = None

    def authenticate(self):
        self._logger.info('Authenticating CVMS user.')
        if self._session.get_cvms_credentials() is None:
            self._logger.fatal('Trying to authenticate with the DIS service without having specified CVMS credentials in the Session constructor.')
        auth_request = CVMS_API.__auth_request(self._session)
        response = auth_request.send()
        if response is None or 'result' not in response or response['result'] != True:
            self._logger.fatal('Error while authenticating CVMS user.')
        bearer = response['data']['authToken']
        customer = Customer(response['data']['user'])
        self._logged_customer = customer
        self._session.store_cvms_bearer(bearer)

    def get_vendor_list(self, page_number=1, items_per_page=100):
        self._logger.info('Getting vendor list')
        request = self.__get_vendor_list(self._session, page_number, items_per_page)
        response_data = request.send()['data']
        return list(map(lambda json: Vendor(json), response_data))

    def get_product_list_from_vendor(self, shop_id, page_number=1, items_per_page=100):
        if shop_id is None:
            self._logger.fatal(f'Trying to acquire products without specifying vendor (shop_id is None).')
        self._logger.info(f'Getting products for vendor {shop_id}')
        request = self.__get_product_list_from_vendor(self._session, shop_id, page_number, items_per_page)
        response_data = request.send()['data']
        if response_data is None:
            return []
        return list(map(lambda json: Product(json), response_data))

    def place_order(self, seller: Vendor, products: [Product]):
        buyer = self._logged_customer
        if buyer is None or seller is None or products is None or len(products) == 0:
            self._logger.fatal(f'Trying to place and order with invalid parameters.')
        self._logger.info(f'Placing order [Buyer: {buyer.name}, Seller: {seller.name}, Products: {products}')
        request = self.__place_order(self._session, buyer, seller, products)
        response_data = request.send()['data']
        return list(map(lambda json: Order(json), response_data))

    def checkout_orders(self, orders: [Order]):
        if orders is None:
            self._logger.fatal(f'Trying to checkout without an order (orders is None).')
        self._logger.info(f'Checking out orders {orders}')
        return self.__checkout_order(self._session, [o.id for o in orders]).send()