DEPENDENCIES_FOLDER="./Dependencies";
VENV_LOCATION="./venv";

sh prepare_venv.sh $VENV_LOCATION
sh install_py_deps.sh $DEPENDENCIES_FOLDER $VENV_LOCATION
sh install_simulator.sh $DEPENDENCIES_FOLDER
sh get_px4_fork.sh