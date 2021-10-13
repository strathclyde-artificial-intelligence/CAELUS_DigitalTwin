import os
from dotenv import load_dotenv
from PySmartSkies.CVMS_API import CVMS_API
from PySmartSkies.Credentials import CVMS_Credentials
from PySmartSkies.Session import Session

# Expects a '.env' file in the examples folder.
# WARNING - If you just pulled from GitHub this file will be MISSING
# You can either replace the CVMS_Credentials below with hardcoded values or
# create the .env file containing the correct credentials (See https://github.com/H3xept/CAELUS_SmartSkies#credentials-setup for the expected format)
load_dotenv()

cvms_credentials = CVMS_Credentials(
    os.environ['CVMS_PHONE'],
    os.environ['CVMS_PASSWORD'],
    os.environ['CVMS_DEVICE_ID']
)

# Alternatively:
# cvms_credentials = CVMS_Credentials(
#     grant_type,
#     your_client_id,
#     your_cvms_username,
#     your_cvms_password
# )

def authenticate_cvms():
    session = Session(cvms_credentials, None)
    api = CVMS_API(session)
    api.authenticate()
    return api

authenticated_api = authenticate_cvms()
