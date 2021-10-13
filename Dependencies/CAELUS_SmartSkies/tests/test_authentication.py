from PySmartSkies.CVMS_API import CVMS_API
from PySmartSkies.DIS_API import DIS_API
from PySmartSkies.Session import Session
from credentials import cvms_credentials, dis_credentials

def test_authenticate_cvms():
    session = Session(cvms_credentials, dis_credentials)
    api = CVMS_API(session)
    api.authenticate()
    assert session.is_cvms_authenticated()
    
def test_authenticate_dis():
    session = Session(cvms_credentials, dis_credentials)
    api = DIS_API(session)
    api.authenticate()
    assert session.is_dis_authenticated()
