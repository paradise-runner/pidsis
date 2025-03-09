#!/bin/bash

# pull pidstats
./pull_pidstats.sh

if [ $? -ne 0 ]; then
    echo "Error: Failed to pull pidstats."
    exit 1
fi

# process pidstats data
uv run main.py /Users/edwardchampion/git/off-coding/pidsis/pidsis/data/pidstats.log

if [ $? -ne 0 ]; then
    echo "Error: Failed to process pidstats data."
    exit 1
fi

# run the web server
uv run run_app.py