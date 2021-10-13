# CAELUS_ProbeSystem
The probe system for the CAELUS architecture

# Installing the module
Open a terminal instance and `cd` inside the CAELUS_ProbeSystem folder.

## Optional - Setting up a virtual environment
To setup a local virtual environment run `python3 -m venv venv`.
This command will create a folder named `venv` in the root directory of the project.

* To **activate** the virtual environment run `source venv/bin/activate`
* To **deactivate** the virtual environment run `deactivate`

## Install dependencies
To install the dependencies required for the probe system run `pip3 install -r requirements.txt`

# Running the probe system
To run the probe system it is enough to issue the command `python3 start.py`.

The default behavior of the program is to listen locally for a drone system. Once a system is discovered, workers are spawned for each supported telemetry endpoint (`see probe_system/helper_data/streams.py` for a complete list of endpoints).

Telemetry endpoints publish new data to all subscribers every time a new datapoint is received.

## Writing a custom probe
Probes are instances of the `Subscriber` abstract class (`helper_data/subscriber.py`).
A probe is capable of receiving datapoints from any of the available endpoints.

A minimal probe example can be found in the `probe_system/probes/echo_subscriber.py` file.

## Writing a custom endpoint pipeline
TBA


