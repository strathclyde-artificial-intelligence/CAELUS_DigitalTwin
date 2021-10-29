DEPENDENCIES_FOLDER="./Dependencies";

sh prepare_venv.sh
sh install_py_deps.sh $DEPENDENCIES_FOLDER
sh install_simulator.sh $DEPENDENCIES_FOLDER
sh get_px4_fork.sh