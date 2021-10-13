# PySmartSkies
[CAELUS] Python SDK for SmartSkies platform.  

# Installing the Library
To install the library environment-wide you can run `pip3 install .`.
This command allows you to use *PySmartSkies* by importing it as shown below:

```python
import PySmartSkies
# or
from PySmartSkies import DIS_API, CVMS_API
```

**Beware** that installing the library does not guarantee that all dependencies will be available at runtime.
Make sure to have all dependencies installed by following the instructions in the **Dependencies** section.

# Dependencies
To install the required dependencies issue `pip3 install -r requirements.txt`.

# Credentials setup
To avoid pushing sensitive data to the GitHub repo, this project makes use of .env files for tests.
Create a `.env.test` file in the root directory of the project.
The file must contain the authentication information for the test accounts (CVMS and DIS).

Here's an example `.env.test` file:

```
DIS_GRANT_TYPE=<grant_type>
DIS_CLIENT_ID=<client_id>
DIS_USERNAME=<your_username>
DIS_PASSWORD=<your_password>
CVMS_PHONE=<your_phone>
CVMS_PASSWORD=<your_password>
CVMS_DEVICE_ID=<your_client_id>
```

# Running tests
From the project's root folder, issue `python3 -m pytest`.

# Workflow

The typical workflow includes:
1. Creating **DIS_Credentials** and **CVMS_Credentials** objects with your *SmartSkies* credentials.
2. Importing and initialising the **Session** module (PySmartSkies.Session)
3. Importing and initialising the required API wrapper (DIS or CVMS) with the previously created *Session* object.
4. Authenticating the API wrapper (`api.authenticate()`)

A minimal authentication example can be found in `examples/minimal_dis.py` for the DIS module and in `examples/minimal_cvms.py` for the CVMS module.

**The example files rely on PySmartSkies being installed in the current environment (See Installing the Library)**