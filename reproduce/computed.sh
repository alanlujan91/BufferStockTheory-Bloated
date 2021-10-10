#!/bin/bash

scriptDir="$(dirname "$0")"
cd "$scriptDir/.."

echo '' ; echo 'Installing requirements' ; echo ''
[[ ! -e binder/requirements.out ]] && pip install -r binder/requirements.txt | tee binder/requirements.out 

echo '' ; echo 'Producing figures' ; echo ''

cd "."
ipython BufferStockTheory.ipynb

[[ -e latexdefs.tex ]] && rm -f latexdefs.tex # Delete junk file that might be created

cd "Code/Python"
./test_Harmenbergs_method.sh



