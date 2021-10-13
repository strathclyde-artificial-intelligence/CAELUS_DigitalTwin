from .Logger import Logger

class Session():
    def __init__(self, cvms_credentials, dis_credentials, logger=Logger()):

        # Session must be initialised with valid CVMS and DIS credentials
        if cvms_credentials is None:
            self.__logger.fatal('CVMS_Credentials are empty in Session constructor.')
        if dis_credentials is None:
            self.__logger.fatal('DIS_Credentials are empty in Session constructor.')

        self.__cvms_credentials = cvms_credentials
        self.__dis_credentials = dis_credentials

        self.__dis_bearer = False
        self.__cvms_bearer = False
        self.__logger = logger
    
    def store_cvms_bearer(self, bearer):
        if bearer is None:
            self.__logger.warn('Trying to store an empty bearer token (CVMS) -- skipping.')
        else:
            self.__cvms_bearer = bearer

    def store_dis_bearer(self, bearer):
        if bearer is None:
            self.__logger.warn('Trying to store an empty bearer token (DIS) -- skipping.')
        else:
            self.__dis_bearer = bearer

    def get_cvms_token(self):
        return self.__cvms_bearer

    def get_dis_token(self):
        return self.__dis_bearer

    def get_cvms_credentials(self):
        return self.__cvms_credentials
    
    def get_dis_credentials(self):
        return self.__dis_credentials

    def is_cvms_authenticated(self):
        return self.get_cvms_token() is not None

    def is_dis_authenticated(self):
        return self.get_dis_token() is not None