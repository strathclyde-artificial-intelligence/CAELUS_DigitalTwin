echo "[🍴] Fethcing CAELUS fork for PX4-Autopilot"
if [ ! -d "/.PX4-Autopilot" ]
    git clone https://github.com/strathclyde-artificial-intelligence/PX4-Autopilot --recurse-submodules
fi