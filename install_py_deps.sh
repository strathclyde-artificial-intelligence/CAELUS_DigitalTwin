DEPENDENCIES_FOLDER=$1

PROBE_SYSTEM="${DEPENDENCIES_FOLDER}/CAELUS_ProbeSystem";
THERMAL_MODEL="${DEPENDENCIES_FOLDER}/CAELUS_ThermalModel";
SMARTSKIES="${DEPENDENCIES_FOLDER}/CAELUS_SmartSkies";
POWER_MODELS="${DEPENDENCIES_FOLDER}/CAELUS_PowerModels";

echo "[🚚] Installing Python Dependencies";
echo "- Installing Probe System"
pip3 install $PROBE_SYSTEM --upgrade
echo "- Installing Thermal Model"
pip3 install $THERMAL_MODEL --upgrade
echo "- Installing Smartskies SDK"
pip3 install $SMARTSKIES --upgrade
echo "- Installing Power Models"
pip3 install $POWER_MODELS --upgrade
