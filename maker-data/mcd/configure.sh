#!/bin/bash

# MCD

mkdir -p latest-data/maker-processed

# get data

python3 get_core_maker_logs.py

# process data

python3 parse_maker_logs.py

python3 calc_cdp_state.py

python3 maker_fees.py

python3 maker_spot_prices.py
