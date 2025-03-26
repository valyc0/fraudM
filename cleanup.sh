#!/bin/bash

# Check if "all" parameter is provided
if [ "$1" = "all" ]; then
    echo "Cleaning up all containers, volumes, networks, and CSV files..."
    # Remove all CSV files from data directory with sudo
    sudo rm -f data/*.csv
    sudo rm -f data/generated_script.py data/temp_script.py
    echo "CSV files cleaned up!"
else
    echo "Cleaning up all containers, volumes, and networks..."
fi

docker-compose down --volumes --remove-orphans

echo "Cleanup complete!"