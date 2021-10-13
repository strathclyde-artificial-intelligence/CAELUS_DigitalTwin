from abc import ABC, abstractmethod
from enum import Enum
import requests
from .Logger import Logger

class BodyType(Enum):
    JSON = 1
    FORM_ENCODED = 2
    RAW = 3

BodyTypeEncodings = {
    BodyType.JSON:{'Content-Type':'application/json'},
    BodyType.FORM_ENCODED:{'Content-Type':'application/x-www-form-urlencoded'},
    BodyType.RAW:{}
}

class Request(ABC):
    def __init__(self, endpoint, payload, logger=Logger()):
        self._endpoint = endpoint
        self._payload = payload
        self._logger = logger
        if not (type(payload) is dict):
            self._logger.warn(f'The request payload for endpoint `{endpoint}` is not a dictionary (Expected key:value pairs).')

    @abstractmethod
    def generate_headers(self):
        pass
    
    @abstractmethod
    def execute_request(self):
        pass

    def send(self, must_succeed=False, jsonify=True):
        response = self.execute_request()
        if response.status_code != requests.codes.ok:
            logging_method = self._logger.fatal if must_succeed else self._logger.warn
            logging_method(f'Request at endpoint `{self._endpoint}` failed (Status code {response.status_code}).')
            return None
        return response.json() if jsonify else response.content


class GET_Request(Request):
    def __init__(self, endpoint, payload, bearer_token=None, logger=Logger()):
        super().__init__(endpoint, payload, logger=logger)
        self.__bearer_token = bearer_token

    def generate_headers(self):
        authorisation_header = {'Authorization':f'{self.__bearer_token}'} if self.__bearer_token is not None else {}
        return {**{'Accept':'*/*'}, **authorisation_header}

    def execute_request(self):
        return requests.get(self._endpoint, params=self._payload, headers=self.generate_headers())
    

class POST_Request(Request):
    def __init__(self, endpoint, payload, bearer_token=None, body_type=BodyType.JSON, logger=Logger()):
        super().__init__(endpoint, payload, logger=logger)
        self.__bearer_token = bearer_token
        self._body_type = body_type

    def generate_headers(self):
        authorisation_header = {'Authorization':f'{self.__bearer_token}'} if self.__bearer_token is not None else {}
        return {
            **{'Accept-Encoding':'gzip, deflate, br', 'Connection':'keep-alive'},
            **BodyTypeEncodings[self._body_type],
            **authorisation_header
        }
            
    def execute_request(self):
        if self._body_type == BodyType.JSON:
            return requests.post(self._endpoint, json=self._payload, headers=self.generate_headers())
        else:
            return requests.post(self._endpoint, data=self._payload, headers=self.generate_headers())