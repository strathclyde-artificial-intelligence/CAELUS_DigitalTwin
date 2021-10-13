import os
from dotenv import load_dotenv
from PySmartSkies.DIS_API import DIS_API
from PySmartSkies.Credentials import DIS_Credentials
from PySmartSkies.Session import Session

# Expects a '.env' file in the examples folder.
# WARNING - If you just pulled from GitHub this file will be MISSING
# You can either replace the DIS_Credentials below with hardcoded values or
# create the .env file containing the correct credentials (See https://github.com/H3xept/CAELUS_SmartSkies#credentials-setup)
load_dotenv()

dis_credentials = DIS_Credentials(
    os.environ['DIS_GRANT_TYPE'],
    os.environ['DIS_CLIENT_ID'],
    os.environ['DIS_USERNAME'],
    os.environ['DIS_PASSWORD']
)

# Alternatively:
# dis_credentials = DIS_Credentials(
#     grant_type,
#     your_client_id,
#     your_dis_username,
#     your_dis_password
# )

def authenticate_dis():
    session = Session(None, dis_credentials)
    api = DIS_API(session)
    api.authenticate()
    return api

authenticated_api = authenticate_dis()
