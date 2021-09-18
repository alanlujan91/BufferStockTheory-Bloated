#!/bin/bash

scriptDir="$(dirname "$0")"
cd "$scriptDir/.."

echo '' ; echo 'Installing requirements' ; echo ''
[[ ! -e binder/requirements.out ]] && pip install -r binder/requirements.txt | tee binder/requirements.out 

echo '' ; echo 'Producing figures' ; echo ''

cd "."
ipython BufferStockTheory.ipynb

