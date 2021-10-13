from abc import ABC, abstractmethod
from Logger import Logger

class API(ABC):

    def _send_request(self, request, must_succeed=True, jsonify=True):
        if not self._session.is_cvms_authenticated():
            self._logger.fatal('Attempted to send a request without being authenticated. Have you issued `api.authenticate()` ?')
        return request.send(must_succeed=True, jsonify=True)
    
    @abstractmethod
    def authenticate(self):
        pass
