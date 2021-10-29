PX4_DIR=./Dependencies/PX4-Autopilot
echo "[🍴] Fethcing CAELUS fork for PX4-Autopilot"
if [ ! -d $PX4_DIR ]; then
    git clone https://github.com/strathclyde-artificial-intelligence/PX4-Autopilot $PX4_DIR --recursive
    (cd $PX4_DIR; make)
fi

echo "[🚚] Installing PX4-Autpilot python dependencies"
pip3 install -r px4_python_requirements.txt