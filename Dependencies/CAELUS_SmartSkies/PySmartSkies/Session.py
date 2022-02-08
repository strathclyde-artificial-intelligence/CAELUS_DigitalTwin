from .Logger import Logger
import time

class Session():
    
    @staticmethod
    def with_tokens(dis_token, dis_refresh_token, cvms_token):
        s = Session(None, None)
        s.store_dis_bearer(dis_token, dis_refresh_token, time.time())
        s.store_cvms_bearer(cvms_token)
        return s

    def __init__(self, cvms_credentials, dis_credentials, logger=Logger()):
        
        self.__logger = logger
        # Session must be initialised with valid CVMS and DIS credentials
        # unless using the "with_tokens" static initialiser
        if cvms_credentials is None:
            self.__logger.warn('CVMS_Credentials are empty in Session constructor.')
        if dis_credentials is None:
            self.__logger.warn('DIS_Credentials are empty in Session constructor.')

        self.__cvms_credentials = cvms_credentials
        self.__dis_credentials = dis_credentials

        self.__dis_bearer = False
        self.__dis_bearer_expiry = 0
        self.__cvms_bearer = False
    
    def set_refresh_closure(self, r):
        self.__refresh_closure = r
        
    def store_cvms_bearer(self, bearer):
        if bearer is None:
            self.__logger.warn('Trying to store an empty bearer token (CVMS) -- skipping.')
        else:
            self.__logger.info(f'Storing CVMS tokens.')
            self.__cvms_bearer = bearer

    def store_dis_bearer(self, bearer, refresh_token, expiry):
        if time.time() > expiry:
            self.__logger.warn(f'Token expiry set to the past ({expiry})! This will trigger an immediate token refresh during the next request.')
        if bearer is None:
            self.__logger.warn('Trying to store an empty bearer token (DIS) -- skipping.')
        else:
            self.__logger.info(f'Storing DIS tokens (Expiry {expiry}).')
            self.__dis_bearer = bearer
            self.__dis_refresh_token = refresh_token
            self.__dis_bearer_expiry = expiry

    def get_cvms_token(self):
        return self.__cvms_bearer

    def get_dis_token(self):
        if time.time() >= self.__dis_bearer_expiry:
            self.__logger.warn('dis token expired. Re-issueing token...')
            if self.__refresh_closure is None:
                self.__logger.fatal('Tried to refresh token but refrsh closure is not defined.')
            else:
                self.__refresh_closure()
        return self.__dis_bearer

    def get_dis_refresh_token(self):
        return self.__dis_refresh_token
    
    def get_cvms_credentials(self):
        return self.__cvms_credentials
    
    def get_dis_credentials(self):
        return self.__dis_credentials

    def is_cvms_authenticated(self):
        return self.get_cvms_token() is not None

    def is_dis_authenticated(self):
        return self.get_dis_token() is not None