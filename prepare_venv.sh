#!/bin/bash 

VENV_LOCATION=$1;

if ! [[ -d $VENV_LOCATION ]]; then
    echo "Virtual environment not present. Creating virtual environment named 'venv' at $VENV_LOCATION.";
    python3 -m venv $VENV_LOCATION;
fi