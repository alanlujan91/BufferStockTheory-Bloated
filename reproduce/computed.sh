#!/bin/bash

scriptDir="$(dirname "$0")"
cd "$scriptDir/.."
pip install -r binder/requirements.txt

cd "Code/Python"
ipython BufferStockTheory-Problems-and-Solutions-Source.ipynb

