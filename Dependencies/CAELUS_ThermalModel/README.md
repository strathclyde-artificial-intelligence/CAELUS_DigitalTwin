# CAELUS_ThermalModel
A python port of the thermal model developed for the CAELUS project by Gianluca Filippi. 

# Installing Dependencies (Development)

To install dependencies run `pip3 install -r requirements.txt`.
**It is advised to use a virtual environment (`python3 -m venv venv`). Activate using `source venv/bin/activate`. Deactivate using `deactivate`**

# Running tests
To run tests, execute `python3 -m pytest -s` from the root folder of the project.

# Writing new tests
To write new tests, add a `.py` file in the `tests` folder. The name of the file must start with `test_`.
Every function in the test file that starts with the `test_` prefix will be used as a test candidate.1