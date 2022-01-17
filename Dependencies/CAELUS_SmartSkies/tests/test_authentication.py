from PySmartSkies.CVMS_API import CVMS_API
from PySmartSkies.DIS_API import DIS_API
from PySmartSkies.Session import Session
from credentials import cvms_credentials, dis_credentials

session = Session(cvms_credentials, dis_credentials)
def test_authenticate_cvms():
    api = CVMS_API(session)
    api.authenticate()
    assert session.is_cvms_authenticated()
    
def test_authenticate_dis():
    api = DIS_API(session)
    api.authenticate()
    assert session.is_dis_authenticated()

def test_refresh_dis():
    api = DIS_API(session)
    api.refresh_token()
    assert session.is_dis_authenticated()
