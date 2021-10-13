from dataclasses import dataclass

@dataclass
class DIS_Credentials():
    grant_type: str
    client_id: str
    username: str
    password: str


@dataclass
class CVMS_Credentials():
    phone: str
    password: str
    device_id: str
