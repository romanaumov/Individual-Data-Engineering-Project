#!/bin/bash
cd /home/ubuntu/iCycleWays
source myvenv/bin/activate

# Get data from source
python3 cycle_lines.py >> ./logs/get_data.log 2>> ./logs/get_data_error.log

# Insert metadata into DB
python3 insert_attributes.py >> ./logs/insert_metadata.log 2>> ./insert_metadata_error.log


