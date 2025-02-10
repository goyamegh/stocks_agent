#!/bin/bash

# Change to the directory containing the script
cd "/Users/goyamegh/workplace/stock_market_agent"

# Activate the virtual environment
source venv/bin/activate

# Run the Python script with the config file
python src/stock_agent.py configs/config_nse.json

# Deactivate the virtual environment
deactivate

# Log the execution time
echo "Stock Market Agent ran at $(date)" >> /Users/goyamegh/workplace/stock_market_agent/logs/execution_log.txt

