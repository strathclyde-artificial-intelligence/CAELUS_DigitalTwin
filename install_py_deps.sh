DEPENDENCIES_FOLDER=$1
VENV_LOCATION=$2

PROBE_SYSTEM="${DEPENDENCIES_FOLDER}/CAELUS_ProbeSystem";
THERMAL_MODEL="${DEPENDENCIES_FOLDER}/CAELUS_ThermalModel";
SMARTSKIES="${DEPENDENCIES_FOLDER}/CAELUS_SmartSkies";
POWER_MODELS="${DEPENDENCIES_FOLDER}/CAELUS_PowerModels";
declare -a PYTHON_DEPS=($PROBE_SYSTEM $THERMAL_MODEL $SMARTSKIES $POWER_MODELS)

echo "[🚚] Installing Python Dependencies";
for DEP in ${PYTHON_DEPS[@]};
do 
    echo "- Installing ${DEP##*/}"
    ${VENV_LOCATION}/bin/pip3 install $DEP --upgrade
    echo "- Installing ${DEP##*/}'s Dependencies"
    ${VENV_LOCATION}/bin/pip3 install -r "${DEP}/requirements.txt"
done

echo "[🚚] Installing DigitalTwin Python Dependencies"
${VENV_LOCATION}/bin/pip3 install -r "requirements.txt"