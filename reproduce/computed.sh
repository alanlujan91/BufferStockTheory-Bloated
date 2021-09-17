#!/bin/bash

scriptDir="$(dirname "$0")"
cd "$scriptDir/.."

echo '' ; echo 'Installing requirements' ; echo ''
[[ ! -e binder/requirements.out ]] && pip install -r binder/requirements.txt | tee binder/requirements.out 

echo '' ; echo 'Producing figures' ; echo ''

cd "Code/Python"
ipython BufferStockTheory-Problems-and-Solutions-Source.ipynb

