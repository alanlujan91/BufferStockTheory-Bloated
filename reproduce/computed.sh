#!/bin/bash

scriptDir="$(dirname "$0")"
cd "$scriptDir/.."

echo '' ; echo 'Installing requirements' ; echo ''
pip install -r binder/requirements.txt

echo '' ; echo 'Producing figures' ; echo ''

cd "Code/Python"
ipython BufferStockTheory-Problems-and-Solutions-Source.ipynb

