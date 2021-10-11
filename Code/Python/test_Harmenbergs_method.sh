#!/bin/bash

if [ ! -e requirements_Harmenberg.out ]; then
    pip freeze --user > requirements_user.txt # Store original setup
    pip install --user -r requirements_Harmenberg.txt > requirements_Harmenberg.out
fi

pushd .
cd src/econ-ark/HARK/ConsumptionSaving/tests
pytest --log-cli-level=DEBUG test_IndShockConsumerType.py -k test_Harmenbergs_method
popd 

# Restore original setup
pip install --user -r requirements_user.txt
