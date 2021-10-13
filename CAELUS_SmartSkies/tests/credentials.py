import os 
# Make sure to have a .test_env file in the root folder
from dotenv import load_dotenv
tests_folder = '/'.join(os.path.abspath(__file__).split('/')[:-1])
config = load_dotenv(tests_folder+'/../.env.test')

from PySmartSkies.Credentials import DIS_Credentials,CVMS_Credentials

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