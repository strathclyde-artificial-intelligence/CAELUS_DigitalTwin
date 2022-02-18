# CAELUS Digital Twin
This repo consists of all components for the Digital Twin architecture (CAELUS).

# Installation
The installation script `install_all.sh` will take care of installing all dependencies.
Issue `sh install_all.sh` to install every dependency.

**WARNING**: After any change to a dependency you **must** re-install that dependency (for simplicityt, re-run `sh install_all.sh`).

# GIT Workflow
This repository uses the [git-subrepo](https://github.com/ingydotnet/git-subrepo) package to track multiple repos.
Editing a subrepo (all folders in `Dependencies`) and pushing it to the upstream will result in the code for that subrepo's repo to be updated.

The used subrepos are the following:

* [CAELUS_SmartSkies](https://github.com/H3xept/CAELUS_SmartSkies) [![PySmartSkies Test](https://github.com/H3xept/CAELUS_SmartSkies/actions/workflows/python-app.yml/badge.svg)](https://github.com/H3xept/CAELUS_SmartSkies/actions/workflows/python-app.yml)
* [CAELUS_ProbeSystem](https://github.com/strathclyde-artificial-intelligence/CAELUS_ProbeSystem/)
* [CAELUS_ThermalModel](https://github.com/strathclyde-artificial-intelligence/CAELUS_ThermalModel)
* [CAELUS_PowerModels](https://github.com/strathclyde-artificial-intelligence/CAELUS_PowerModels) [![PyPowerModels Test](https://github.com/strathclyde-artificial-intelligence/CAELUS_PowerModels/actions/workflows/python-app.yml/badge.svg)](https://github.com/strathclyde-artificial-intelligence/CAELUS_PowerModels/actions/workflows/python-app.yml)

## Pulling new changes
To pull all changes from all the dependencies & the main repo, issue `git subrepo pull --all`.
One can additionally pull from a single subrepo with the command `git subrepo pull Dependencies/<subrepo_name>`

## Pushing New Changes
To push all changes from all the dependencies & the main repo, issue `git subrepo push --all`.
One can additionally push from a single subrepo with the command `git subrepo push Dependencies/<subrepo_name>`

# Development

## Writing startup scripts 

## Drone configurations

Drone configurations are stored in the `available_drones` folder.
By default the supported vehicle types are `QUADCOPTER` and `EVTOL_FW` (This value is used across the simulation stack to determine the vehicle type).

### Adding a new drone

To add a new drone configuration:

1. Add a `.json` file in the `available_drones` folder with the example specified below:

```json

{
    "id": "evtol_fw_large",
    "name": "EVTOL FW Large",
    "px4_airframe_reference": "custom_evtolfw_large",
    "type": "EVTOL_FW",
    "aerodynamics": {
        "wing_span": 2.1,
        "wing_area": 0.8,
        "mean_aerodynamic_chord": 0.357,
        "m_CL_0": 0.0477,
        "m_CL_alpha": 4.06,
        "m_CL_delta_e": 0.7,
        "m_CL_q": 3.87,
        "m_CD_0": 0.0107,
        "m_CD_alpha": -0.00955,
        "m_CD_alpha2": 1.1,
        "m_CD_delta_e2": 0.0196,
        "m_CD_beta2": 0,
        "m_CD_beta": 0.115,
        "m_CD_q": 0,
        "m_CS_0": 0,
        "m_CS_beta": -0.194,
        "m_CS_delta_a": 0.0439,
        "m_CS_delta_r": 0,
        "m_CS_p": -0.137,
        "m_CS_r": 0.0839,
        "m_Cm_0": 0.00439,
        "m_Cm_alpha": -0.227,
        "m_Cm_delta_e": -0.325,
        "m_Cm_q": -1.3,
        "m_Cl_0": 0,
        "m_Cl_beta": -0.0751,
        "m_Cl_delta_a": 0.202,
        "m_Cl_delta_r": 0,
        "m_Cl_p": -0.404,
        "m_Cl_r": 0.0555,
        "m_Cn_0": 0,
        "m_Cn_beta": 0.0312,
        "m_Cn_delta_a": -0.00628,
        "m_Cn_delta_r": 0,
        "m_Cn_p": 0.00437,
        "m_Cn_r": -0.012
    },
    "drone_config": {
        "mass": 2.0,
        "arm_length": 0.25,
        "max_rpm": 13000,
        "max_torque": 0.10,
        "propeller_specs": {
            "diameter_cm": 18.0,
            "pitch_cm": 13.0,
            "blades_n": 3
        },
        "drag_move": 0.028,
        "Ixx": 0.335,
        "Iyy": 0.14,
        "Izz": 0.4,
        "Ixz": -0.029,
        "Izx": -0.029
    }
}

```

**NOTE**: "px4_airframe_parameters" contains non-standard parameters for the new airframe. Dependeing on the drone type there are some defaults specified in the PX4 fork airframe files `4200_custom_quad` and `4201_custom_evtol`.

2. Run the `sync_custom_px4_vehicles.py` script: `python3 sync_custom_px4_vehicles.py`

The new configuration will now be available in the digital twin. See [Writing startup scripts](#writing-startup-scripts) for the appropriate parameter to use.

# Tooling