# Savings Data from Tesla

This is a python 2.7 script for gathering historical data

## Dependencies

import requests

## Set Env Variables

export SAVINGS_HOST=somehost
export SAVINGS_USER=someusername
export SAVINGS_PASSWORD=somesecretpassword
export SAVINGS_STATION_ID=0e629fed-9345-4a40-ba90-a2f825b89a14 (tesla station id)
export SAVINGS_REPORT_PATH='/dir/subdir' (directory to store "history.csv")

## To Run
python savings_data_script.py 2019-06-01T00.00.00.000-07.00 2019-06-01T00.00.00.000-07.00 "America/Phoenix"
