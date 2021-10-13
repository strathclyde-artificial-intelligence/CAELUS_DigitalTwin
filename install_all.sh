VENV_LOCATION="./venv";

if ! [[ -d $VENV_LOCATION ]]; then
    echo "Virtual environment not present. Creating virtual environment named 'venv' at $VENV_LOCATION.";
    python3 -m venv $VENV_LOCATION;
fi
[[ "$VIRTUAL_ENV" == "" ]]; INVENV=$?

if [ !$INVENV ]; then
    echo "Activating virtual environment ($VENV_LOCATION)";
    source "${VENV_LOCATION}/bin/activate";
fi

DEPENDENCIES_FOLDER="./Dependencies";
PROBE_SYSTEM="${DEPENDENCIES_FOLDER}/CAELUS_ProbeSystem";
THERMAL_MODEL="${DEPENDENCIES_FOLDER}/CAELUS_ThermalModel";
SMARTSKIES="${DEPENDENCIES_FOLDER}/CAELUS_SmartSkies";
POWER_MODELS="${DEPENDENCIES_FOLDER}/CAELUS_PowerModels";
SIMULATOR="${DEPENDENCIES_FOLDER}/Simulator"

echo "Installing Python Dependencies";
pip3 install $PROBE_SYSTEM --upgrade
pip3 install $THERMAL_MODEL --upgrade
pip3 install $SMARTSKIES --upgrade
pip3 install $POWER_MODELS --upgrade

echo "Installing Simulator"
$(cd $SIMULATOR; bash setup.sh;);
