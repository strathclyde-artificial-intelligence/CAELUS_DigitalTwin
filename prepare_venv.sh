VENV_LOCATION="./venv";
read -e -p "Preferred python virtual environment location: (default $VENV_LOCATION)" input
VENV_LOCATION="${input:-$VENV_LOCATION}"


if ! [[ -d $VENV_LOCATION ]]; then
    echo "Virtual environment not present. Creating virtual environment named 'venv' at $VENV_LOCATION.";
    python3 -m venv $VENV_LOCATION;
fi
[[ "$VIRTUAL_ENV" == "" ]]; INVENV=$?

if [ !$INVENV ]; then
    echo "Activating virtual environment ($VENV_LOCATION)";
    source "${VENV_LOCATION}/bin/activate";
fi