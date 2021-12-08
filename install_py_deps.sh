DEPENDENCIES_FOLDER=$1

PROBE_SYSTEM="${DEPENDENCIES_FOLDER}/CAELUS_ProbeSystem";
THERMAL_MODEL="${DEPENDENCIES_FOLDER}/CAELUS_ThermalModel";
SMARTSKIES="${DEPENDENCIES_FOLDER}/CAELUS_SmartSkies";
POWER_MODELS="${DEPENDENCIES_FOLDER}/CAELUS_PowerModels";
declare -a PYTHON_DEPS=($PROBE_SYSTEM $THERMAL_MODEL $SMARTSKIES $POWER_MODELS)

echo "[🚚] Installing Python Dependencies";
for DEP in ${PYTHON_DEPS[@]};
do 
    echo "- Installing ${DEP##*/}"
    pip3 install $DEP --upgrade
    echo "- Installing ${DEP##*/}'s Dependencies"
    pip3 install -r "${DEP}/requirements.txt"
done

echo "[🚚] Installing DigitalTwin Python Dependencies"
pip3 install -r "requirements.txt"