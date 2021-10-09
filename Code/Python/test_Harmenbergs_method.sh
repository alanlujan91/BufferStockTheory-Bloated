#!/bin/bash

pip install -r ./binder/requirements.txt > ./binder/requirements.out
cd src/econ-ark/HARK/HARK/tests
pytest --log-cli-level=DEBUG test_IndShockConsumerType.py -k test_Harmenbergs_method
